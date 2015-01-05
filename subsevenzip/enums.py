# Copyright (c) 2015, Daniel Svensson <dsvensson@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

from enum import Enum, IntEnum


class PropertyId(IntEnum):
    kEnd = 0x00
    kHeader = 0x01
    kArchiveProperties = 0x02
    kAdditionalStreamsInfo = 0x03
    kMainStreamsInfo = 0x04
    kFilesInfo = 0x05
    kPackInfo = 0x06
    kUnpackInfo = 0x07
    kSubStreamsInfo = 0x08
    kSize = 0x09
    kCRC = 0x0a
    kFolder = 0x0b
    kCodersUnpackSize = 0x0c
    kNumUnpackStream = 0x0d
    kEmptyStream = 0x0e
    kEmptyFile = 0x0f
    kAnti = 0x10
    kName = 0x11
    kCTime = 0x12
    kATime = 0x13
    kMTime = 0x14
    kWinAttributes = 0x15
    kComment = 0x16
    kEncodedHeader = 0x17
    kStartPos = 0x18
    kDummy = 0x19


class CodecId(bytes, Enum):
    COPY = b'\x00'
    LZMA = b'\x03\x01\x01'
    LZMA2 = b'\x21'
    DEFLATE = b'\x04\x01\x08'
    BZIP2 = b'\x04\x02\x02'
    AES256SHA256 = b'\x06\xf1\x07\x01'
    BCJ_X86_FILTER = b'\x03\x03\x01\x03'
    BCJ_PPC_FILTER = b'\x03\x03\x02\x05'
    BCJ_IA64_FILTER = b'\x03\x03\x04\x01'
    BCJ_ARM_FILTER = b'\x03\x03\x05\x01'
    BCJ_ARM_THUMB_FILTER = b'\x03\x03\x07\x01'
    BCJ_SPARC_FILTER = b'\x03\x03\x08\x05'
    DELTA_FILTER = b'\x03'
