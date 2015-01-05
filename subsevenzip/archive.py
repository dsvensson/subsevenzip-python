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

import lzma
import io
import builtins

from .parser import parse_headers
from .buffer import ReadBuffer
from .codec import open_lzma_stream


class SevenZipArchive(object):
    def __init__(self, factory, files):
        self._factory = factory
        self._stream = None
        self.files = files

    def get_content(self, file):
        if not self._stream:
            self._stream = self._factory()
        try:
            self._stream.seek(file._offset)
            return self._stream.read(file.size)
        except lzma.LZMAError:
            # Seems like it's not possible to seek backward
            self._stream = self._factory()
            self._stream.seek(file._offset)
            return self._stream.read(file.size)


def open(arg):
    if isinstance(arg, bytes):
        close_fd = -1
        buf = ReadBuffer(io.BytesIO(arg))
    elif isinstance(arg, str):
        close_fd = builtins.open(arg, "rb")
        buf = ReadBuffer(close_fd)
    elif hasattr(arg, "read") or hasattr(arg, "write"):
        close_fd = -1
        buf = ReadBuffer(arg)
    else:
        raise ValueError("Can only open a SevenZip archive from filename, bytes, or a file descriptor")

    archive = parse_headers(buf)

    def stream_factory():
        buf.seek(archive["payload_offset"], io.SEEK_SET)
        stream = buf.get_sub_stream(archive["compressed_size"])
        return open_lzma_stream(stream, archive["codec_properties"])

    return SevenZipArchive(stream_factory, archive["files"])
