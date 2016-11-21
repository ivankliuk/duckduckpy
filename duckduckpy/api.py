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

from . import __version__
from .utils import camel_to_snake_case_set

from collections import namedtuple

SERVER_HOST = 'api.duckduckgo.com'
USER_AGENT = 'duckduckpy {0}'.format(__version__)

ICON_KEYS = set(['URL', 'Width', 'Height'])
RESULT_KEYS = set(['FirstURL', 'Icon', 'Result', 'Text'])
RELATED_TOPIC_KEYS = set(['Name', 'Topics'])
RESPONSE_KEYS = set([
    'Redirect', 'Definition', 'ImageWidth', 'Infobox', 'RelatedTopics',
    'ImageHeight', 'Heading', 'Answer', 'AbstractText', 'Type', 'ImageIsLogo',
    'DefinitionSource', 'AbstractURL', 'Abstract', 'DefinitionURL', 'Results',
    'Entity', 'AnswerType', 'AbstractSource', 'Image', 'meta'])
Icon = namedtuple('Icon', camel_to_snake_case_set(ICON_KEYS))
Result = namedtuple('Result', camel_to_snake_case_set(RESULT_KEYS))
RelatedTopic = namedtuple('RelatedTopic',
                          camel_to_snake_case_set(RELATED_TOPIC_KEYS))
Response = namedtuple('Response', camel_to_snake_case_set(RESPONSE_KEYS))
