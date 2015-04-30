# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from . import __version__
from collections import namedtuple
from .utils import camel_to_snake_case

SERVER_HOST = 'api.duckduckgo.com'
USER_AGENT = 'duckduckpy {0}'.format(__version__)

ICON_KEYS = set(['URL', 'Width', 'Height'])
RESULT_KEYS = set(['FirstURL', 'Icon', 'Result', 'Text'])
CONTENT_KEYS = set(['data_type', 'label', 'sort_order', 'value', 'wiki_order'])
META_KEYS = set(['data_type', 'label', 'value'])
INFOBOX_KEYS = set(['content', 'meta'])
RESPONSE_KEYS = set([
    'Redirect', 'Definition', 'ImageWidth', 'Infobox', 'RelatedTopics',
    'ImageHeight', 'Heading', 'Answer', 'AbstractText', 'Type', 'ImageIsLogo',
    'DefinitionSource', 'AbstractURL', 'Abstract', 'DefinitionURL', 'Results',
    'Entity', 'AnswerType', 'AbstractSource', 'Image'])

camel_to_snake_case_set = lambda seq: set(map(camel_to_snake_case, seq))
Icon = namedtuple('Icon', camel_to_snake_case_set(ICON_KEYS))
Result = namedtuple('Result', camel_to_snake_case_set(RESULT_KEYS))
Content = namedtuple('Content', camel_to_snake_case_set(CONTENT_KEYS))
Meta = namedtuple('Meta', camel_to_snake_case_set(META_KEYS))
Infobox = namedtuple('Infobox', camel_to_snake_case_set(INFOBOX_KEYS))
Response = namedtuple('Response', camel_to_snake_case_set(RESPONSE_KEYS))
