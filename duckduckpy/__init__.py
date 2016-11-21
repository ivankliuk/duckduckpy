# -*- coding: utf-8 -*-

"""Library for querying the instant answer API of DuckDuckGo search engine."""

__version__ = 0.2
__author__ = 'Ivan Kliuk'
__email__ = 'ivan.kliuk@gmail.com'
__license__ = 'MIT'
__url__ = 'https://github.com/ivankliuk/duckduckpy/'
__all__ = ['query', 'secure_query']


from duckduckpy.core import query
from duckduckpy.core import secure_query
