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

import io
import struct


class BoundedBufferedReader(io.BufferedReader):
    def __init__(self, stream, limit):
        io.BufferedReader.__init__(self, stream)
        self._limit = limit

    def read(self, size):
        position = super().tell()
        if (position + size) > self._limit:
            return super().read(self._limit - position)
        return super().read(size)

    def close(self):
        # Should not close parent file descriptor
        pass


class ReadBuffer(object):
    def __init__(self, fd):
        assert isinstance(fd, io.IOBase)
        self._fd = fd
        self._pos = 0
        self._limit = None

    def _read(self, func):
        try:
            return func()
        finally:
            self._check_limit()

    def _check_limit(self):
        if self._limit is None:
            return
        if self._fd.tell() > self._limit:
            raise IOError("ReadBuffer limit breached! (limit: %d, position: %d)" % (self._limit, self._fd.tell()))

    def set_limit(self, limit, absolute=False):
        if absolute:
            self._limit = limit
        else:
            self._limit = self._fd.tell() + limit

    def unset_limit(self):
        self._limit = None

    def get_uint8(self):
        return self._read(lambda: struct.unpack("<B", self._fd.read(1))[0])

    def get_uint16(self):
        return self._read(lambda: struct.unpack("<H", self._fd.read(2))[0])

    def get_uint32(self):
        return self._read(lambda: struct.unpack("<I", self._fd.read(4))[0])

    def get_uint64(self):
        return self._read(lambda: struct.unpack("<Q", self._fd.read(8))[0])

    def get_varint(self):
        first_byte = self.get_uint8()
        mask = 0x80
        value = 0
        for x in range(8):
            if (first_byte & mask) == 0:
                return value | ((first_byte & (mask - 1)) << 8 * x)
            value |= self.get_uint8() << 8 * x
            mask >>= 1
        return value

    def get_bits(self, count):
        value = 0
        mask = 0
        cache = 0
        for x in range(count):
            if not mask:
                mask = 0x80
                cache = self.get_uint8()
            value |= int((cache & mask) != 0) << x
            mask >>= 1
        return value

    def get_all_or_bits(self, count):
        all_defined = self.get_uint8()
        if all_defined:
            return (1 << count) - 1
        return self.get_bits(count)

    def get_utf16_le(self):
        buffer = bytearray([])
        while True:
            value1 = self.get_uint8()
            value2 = self.get_uint8()
            if value1 == 0 and value2 == 0:
                return buffer.decode("utf-16-le")
            buffer.append(value1)
            buffer.append(value2)
        raise IOError("UTF-16 string was not \\0 terminated")

    def get_bytes(self, length):
        return self._read(lambda: self._fd.read(length))

    def seek(self, offset, whence=io.SEEK_CUR):
        self._fd.seek(offset, whence)
        self._check_limit()

    def tell(self):
        return self._fd.tell()

    def get_sub_stream(self, length):
        return BoundedBufferedReader(self._fd, self._fd.tell() + length)
