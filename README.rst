SubSevenZip
===========

A 7zip extractor written in python, supports only a subset of the 7zip spec. At the moment only LZMA1 encoding is supported, might add more codecs later. The reason this module exists is just to toy with the format, before writing a JavaScript version that can extract a very well defined set of files.

.. image:: https://secure.travis-ci.org/dsvensson/subsevenzip-python.png?branch=master
    :target: https://travis-ci.org/dsvensson/subsevenzip-python

.. image:: https://coveralls.io/repos/dsvensson/subsevenzip-python/badge.png?branch=master
    :target: https://coveralls.io/r/dsvensson/subsevenzip-python

Related
-------

Some links that were useful during the development of this module.

* http://www.7-zip.org
* https://commons.apache.org/proper/commons-compress
* https://github.com/adamhathcock/sharpcompress

Both Apache CommonsCompress and SharpCompress are pretty much line-by-line ports of the original 7-Zip C++ code.

License
-------
The database composition is free to use under the Internet Software Consortium License,
for additional details see COPYING.ISC.