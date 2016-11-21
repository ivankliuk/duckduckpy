# -*- coding: utf-8 -*-

# The MIT License (MIT)
# Copyright (c) 2015 Ivan Kliuk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import unicode_literals

import re
import sys

_1 = re.compile(r'(.)([A-Z][a-z]+)')
_2 = re.compile('([a-z0-9])([A-Z])')


def is_python2():
    """Checks whether Python major version is 2."""
    return sys.version_info[0] == 2


def camel_to_snake_case(string):
    """Converts 'string' presented in camel case to snake case.

    e.g.: CamelCase => snake_case
    """
    s = _1.sub(r'\1_\2', string)
    return _2.sub(r'\1_\2', s).lower()


def camel_to_snake_case_set(seq):
    """Converts sequence to the snake case and returns the result as set."""
    return set(map(camel_to_snake_case, seq))


def decoder(obj):
    """Decodes 'bytes' object to UTF-8."""
    if isinstance(obj, bytes):
        return obj.decode("utf-8")
    return obj
