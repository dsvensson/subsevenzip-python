# Copyright (c) 2015, Daniel Svensson <dsvensson@gmail.com>
#
#  Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all copies.
#
#  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import io
import struct
import binascii

from .enums import PropertyId, CodecId
from .exceptions import BadSevenZipArchive
from .codec import open_lzma_stream
from .builder import FilesInfoBuilder
from .buffer import ReadBuffer


def parse_pack_info(buf, archive):
    archive["compressed_offset"] = buf.get_varint()
    n_streams = buf.get_varint()
    if n_streams != 1:
        raise NotImplementedError("Only single stream files supported")

    nid = buf.get_uint8()
    if nid == PropertyId.kSize:
        archive["compressed_size"] = buf.get_varint()
        nid = buf.get_uint8()

    if nid == PropertyId.kCRC:
        raise NotImplementedError("CRC for PackInfo not supported")

    if nid != PropertyId.kEnd:
        raise BadSevenZipArchive.mismatch(PropertyId.kEnd, nid)


def parse_folder(buf):
    n_coders = buf.get_varint()
    if n_coders != 1:
        raise NotImplementedError("Only support folders with one coder")

    codec_size = lambda x: x & 0xf
    is_complex = lambda x: (x & 0x10) != 0
    has_properties = lambda x: (x & 0x20) != 0
    has_additional = lambda x: (x & 0x80) != 0

    flags = buf.get_uint8()

    if has_additional(flags):
        raise NotImplementedError("Deprecated 7zip feature")

    codec = CodecId(buf.get_bytes(codec_size(flags)))
    if codec != CodecId.LZMA:
        raise NotImplementedError("Codec %s not supported" % codec)

    if is_complex(flags):
        raise NotImplementedError("Multiple I/O streams not supported")

    if not has_properties(flags):
        raise NotImplementedError("Only LZMA is supported, which has properties")

    properties_size = buf.get_varint()
    properties_bytes = buf.get_bytes(properties_size)

    return codec, properties_bytes


def parse_unpack_info(buf, archive):
    nid = buf.get_uint8()
    if nid != PropertyId.kFolder:
        raise BadSevenZipArchive.mismatch(PropertyId.kFolder, nid)

    n_folders = buf.get_varint()
    if n_folders != 1:
        raise NotImplementedError("Only support one folder structure per archive")

    external = buf.get_uint8()
    if external != 0:
        raise NotImplementedError("External not supported")

    archive["codec"], archive["codec_properties"] = parse_folder(buf)

    nid = buf.get_uint8()
    if nid != PropertyId.kCodersUnpackSize:
        raise BadSevenZipArchive.mismatch(PropertyId.kCodersUnpackSize, nid)

    archive["decompressed_size"] = buf.get_varint()

    nid = buf.get_uint8()
    if nid == PropertyId.kCRC:
        has_crc = buf.get_all_or_bits(n_folders)
        if has_crc > 0:
            archive["checksum"] = buf.get_uint32()
            nid = buf.get_uint8()

    if nid != PropertyId.kEnd:
        raise BadSevenZipArchive.mismatch(PropertyId.kEnd, nid)


def parse_substreams_info(buf, archive):
    nid = buf.get_uint8()
    if nid != PropertyId.kNumUnpackStream:
        raise BadSevenZipArchive.mismatch(PropertyId.kNumUnpackStream, nid)

    n_substreams = buf.get_varint()
    if n_substreams < 1:
        raise NotImplementedError("Only 1...n substreams supported")

    nid = buf.get_uint8()
    if nid != PropertyId.kSize:
        raise BadSevenZipArchive.mismatch(PropertyId.kSize, nid)

    sizes = list()

    accumulated_size = 0
    for x in range(n_substreams - 1):
        size = buf.get_varint()
        sizes.append(size)
        accumulated_size += size

    sizes.append(archive["decompressed_size"] - accumulated_size)

    archive["decompressed_sizes"] = sizes

    nid = buf.get_uint8()
    if nid != PropertyId.kCRC:
        raise BadSevenZipArchive.mismatch(PropertyId.kCRC, nid)

    missing_crc = buf.get_all_or_bits(n_substreams)
    for x in range(n_substreams):
        if ((1 << x) & missing_crc) != 0:
            buf.get_uint32()

    nid = buf.get_uint8()
    if nid != PropertyId.kEnd:
        raise BadSevenZipArchive.mismatch(PropertyId.kEnd, nid)


def parse_streams_info(buf, archive):
    nid = buf.get_uint8()
    if nid != PropertyId.kPackInfo:
        raise BadSevenZipArchive.mismatch(PropertyId.kPackInfo, nid)

    parse_pack_info(buf, archive)

    nid = buf.get_uint8()
    if nid != PropertyId.kUnpackInfo:
        raise BadSevenZipArchive.mismatch(PropertyId.kUnpackInfo, nid)

    parse_unpack_info(buf, archive)

    nid = buf.get_uint8()
    if nid == PropertyId.kSubStreamsInfo:
        parse_substreams_info(buf, archive)
        nid = buf.get_uint8()

    if nid != PropertyId.kEnd:
        raise BadSevenZipArchive("Badly terminated StreamsInfo")

    return archive


def parse_encoded_header(buf, payload_position):
    archive = {}
    parse_streams_info(buf, archive)
    header_offset = payload_position + archive["compressed_offset"]
    buf.seek(header_offset, whence=io.SEEK_SET)
    with open_lzma_stream(buf.get_sub_stream(archive["compressed_size"]), archive["codec_properties"]) as fd:
        return fd.read(archive["decompressed_size"])


def parse_files_info(buf, archive):
    n_files = buf.get_varint()
    fib = FilesInfoBuilder()
    fib.reset(n_files)

    while True:
        nid = buf.get_uint8()
        if nid == PropertyId.kEnd:
            break
        size = buf.get_varint()
        buf.set_limit(size)
        if nid == PropertyId.kEmptyStream:
            fib.set_empty_stream_mask(buf.get_bits(n_files))
        elif nid == PropertyId.kName:
            if buf.get_uint8() != 0:
                raise NotImplementedError("External FilesInfo kName not supported")
            for index in range(n_files):
                fib.set_name(index, buf.get_utf16_le())
        else:
            buf.seek(size)
        buf.unset_limit()

    offset = 0
    it = iter(archive["decompressed_sizes"])

    for index in range(n_files):
        if ((1 << index) & fib.empty_stream_mask) == 0:
            size = next(it)
            fib.set_size(index, size)
            fib.set_offset(index, offset)
            offset += size

    archive["files"] = fib.build()


def parse_header(buf, payload_offset):
    archive = {
        "payload_offset": payload_offset
    }

    nid = buf.get_uint8()
    if nid == PropertyId.kArchiveProperties:
        raise NotImplementedError("ArchiveProperties not supported")

    if nid == PropertyId.kAdditionalStreamsInfo:
        raise NotImplementedError("AdditionalStreamsInfo not supported")

    if nid == PropertyId.kMainStreamsInfo:
        parse_streams_info(buf, archive)
        nid = buf.get_uint8()

    if nid == PropertyId.kFilesInfo:
        parse_files_info(buf, archive)
        nid = buf.get_uint8()

    if nid != PropertyId.kEnd:
        raise BadSevenZipArchive.mismatch(PropertyId.kEnd, nid)

    return archive


def parse_start_header(buf):
    next_header_offset = buf.get_uint64()
    next_header_size = buf.get_uint64()
    next_header_crc = buf.get_uint32()
    return next_header_offset, next_header_size, next_header_crc


def parse_signature_header(buf):
    magic = b'\x37\x7a\xbc\xaf\x27\x1c'
    if magic != buf.get_bytes(6):
        raise BadSevenZipArchive("Bad magic")

    major = buf.get_uint8()
    minor = buf.get_uint8()

    crc = buf.get_uint32()

    start_header = buf.get_bytes(struct.calcsize("QQI"))
    if crc != binascii.crc32(start_header) & 0xffffffff:
        raise BadSevenZipArchive("StartHeader checksum failed")

    return parse_start_header(ReadBuffer(io.BytesIO(start_header)))


def parse_headers(buf):
    next_header_offset, next_header_size, _ = parse_signature_header(buf)

    payload_offset = buf.tell()

    buf.seek(next_header_offset)

    nid = buf.get_uint8()
    if nid != PropertyId.kEncodedHeader:
        raise BadSevenZipArchive.mismatch(PropertyId.kEncodedHeader, nid)

    buf.set_limit(next_header_size)
    decoded_header = ReadBuffer(io.BytesIO(parse_encoded_header(buf, payload_offset)))
    buf.unset_limit()

    nid = decoded_header.get_uint8()
    if nid != PropertyId.kHeader:
        raise BadSevenZipArchive.mismatch(PropertyId.kHeader, nid)

    return parse_header(decoded_header, payload_offset)
