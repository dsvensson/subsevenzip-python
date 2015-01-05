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

import subsevenzip
import unittest
import io

class TestSubSevenZip(unittest.TestCase):
    BASIC = b"\x37\x7a\xbc\xaf\x27\x1c\x00\x03\x3b\x62\xd6\xd8\x6c\x00\x00\x00" \
            b"\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\xb5\x6f\xb6\x47" \
            b"\x00\x3a\x19\x4a\xce\x1f\xa3\x23\x6d\x85\x58\xc8\x10\x88\x45\xa0" \
            b"\x00\x00\x81\x33\x07\xae\x0f\xce\xf2\xb2\x0c\x07\xc8\x43\x80\x83" \
            b"\x81\x5b\xff\xac\x80\x1d\x50\x19\xfc\x6f\x65\x9d\xed\xc4\x81\xfd" \
            b"\x25\x7d\x4b\x61\x0a\x61\x05\x96\x92\x84\x10\x62\x8d\x89\x04\xbf" \
            b"\x09\xa1\x64\x5f\xae\xb7\x96\xfa\xdf\x1a\x2b\xba\x50\x8e\xdc\xb1" \
            b"\xeb\xe5\x27\x8b\xc1\x5c\x10\xba\xf9\x70\x14\x55\xf3\x2e\x2b\x5f" \
            b"\x29\xbf\xb2\x5a\xc4\xc1\xad\xdf\xb6\x00\x00\x00\x17\x06\x10\x01" \
            b"\x09\x5c\x00\x07\x0b\x01\x00\x01\x23\x03\x01\x01\x05\x5d\x00\x10" \
            b"\x00\x00\x0c\x6e\x0a\x01\x8e\xe1\xbf\xaf\x00\x00"

    def test_basic(self):
        stream = io.BytesIO(TestSubSevenZip.BASIC)
        sz = subsevenzip.open(stream)
        self.assertEqual("test_a", sz.files[0].name)
        self.assertEqual(b"test_a\n", sz.get_content(sz.files[0]))
        self.assertEqual("test_b", sz.files[1].name)
        self.assertEqual(b"test_b\n", sz.get_content(sz.files[1]))

if __name__ == '__main__':
    unittest.main()
