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

import lzma

from .exceptions import BadSevenZipArchive


def open_lzma_stream(stream, properties):
    options = properties[0] & 0xff

    pb = int(options / (9 * 5))

    options -= int(pb * 9 * 5)

    # Number of literal position bits.
    lp = int(options / 9)

    # Number of literal context bits.
    lc = int(options - lp * 9)

    # The sum lc + lp must be at most 4.
    if lc + lp > 4:
        raise BadSevenZipArchive("Corrupt LZMA properties")

    dict_size = int(properties[1])
    for x in range(1, 4, 1):
        dict_size |= (properties[x + 1] & 0xff) << (8 * x)

    if not 4096 <= dict_size < (2**30 + 2**29):
        raise BadSevenZipArchive("Corrupt LZMA dictionary size (%d)" % dict_size)

    return lzma.LZMAFile(stream, format=lzma.FORMAT_RAW, filters=[{
        "id": lzma.FILTER_LZMA1,
        "dict_size": dict_size,
        "pb": pb,
        "lp": lp,
        "lc": lc
    }])
