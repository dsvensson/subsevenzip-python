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


class File(object):

    def __init__(self, name, size, offset, has_stream):
        self.name = name
        self.size = size
        self._offset = offset
        self.has_stream = has_stream

    def __repr__(self):
        return "File('%s', size:%d, stream:%s)" % (self.name, self.size, self.has_stream)


class FilesInfoBuilder(object):
    def __init__(self):
        self.reset(0)

    def reset(self, size):
        self.count = size
        self.names = [None] * size
        self.sizes = [0] * size
        self.offsets = [0] * size
        self.empty_stream_mask = 0

    def set_name(self, index, name):
        self.names[index] = name

    def set_size(self, index, size):
        self.sizes[index] = size

    def set_offset(self, index, offset):
        self.offsets[index] = offset

    def set_empty_stream_mask(self, mask):
        self.empty_stream_mask = mask

    def build(self):
        try:
            return [File(self.names[idx], self.sizes[idx], self.offsets[idx], ((1 << idx) & self.empty_stream_mask) == 0) for idx in range(self.count)]
        finally:
            self.reset(0)
