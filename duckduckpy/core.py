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

from . import api
from . import exception as exc
from .utils import camel_to_snake_case
from .utils import is_python2
from .utils import decoder

import functools
import json
import socket

# Python 2/3 compatibility.
if is_python2():
    import httplib as http_client
    from urllib import urlencode
else:
    import http.client as http_client
    from urllib.parse import urlencode


class Hook(object):
    """A hook for dict-objects serialization."""
    containers = ['namedtuple', 'dict']

    def __new__(cls, container, verbose=False):
        if container not in cls.containers:
            if verbose:
                raise exc.DuckDuckDeserializeError(
                    "Deserialization container '{0}'"
                    " is not found".format(container))
            return None
        return super(Hook, cls).__new__(cls)

    def __init__(self, container, verbose=False):
        self._container = container
        self._verbose = verbose

    def _camel_to_snake_case(self):
        keys = set(self.dict_object.keys())
        for key in keys:
            val = self.dict_object.pop(key)
            self.dict_object[camel_to_snake_case(key)] = val

    def serialize(self, class_name):
        self._camel_to_snake_case()
        if self._container == 'namedtuple':
            namedtuple_class = getattr(api, class_name)
            return namedtuple_class(**self.dict_object)
        if self._container == 'dict':
            return self.dict_object

    def __call__(self, dict_object):
        keys = set(dict_object.keys())
        self.dict_object = dict_object
        if not keys:
            return {}
        if keys == api.ICON_KEYS:
            return self.serialize('Icon')
        elif keys == api.RESULT_KEYS:
            return self.serialize('Result')
        elif keys == api.RELATED_TOPIC_KEYS:
            return self.serialize('RelatedTopic')
        elif keys == api.RESPONSE_KEYS:
            return self.serialize('Response')

        # Leave 'meta' object as is.
        uppercase_keys = list(filter(lambda k: k[0].isupper(), keys))
        if not self._verbose or not uppercase_keys:
            return dict_object
        raise exc.DuckDuckDeserializeError(
            "Unable to deserialize dict to an object")


def url_assembler(query_string, no_redirect=0, no_html=0, skip_disambig=0):
    """Assembler of parameters for building request query.

    Args:
        query_string: Query to be passed to DuckDuckGo API.
        no_redirect: Skip HTTP redirects (for !bang commands). Default - False.
        no_html: Remove HTML from text, e.g. bold and italics. Default - False.
        skip_disambig: Skip disambiguation (D) Type. Default - False.

    Returns:
        A “percent-encoded” string which is used as a part of the query.
    """
    params = [('q', query_string.encode("utf-8")), ('format', 'json')]

    if no_redirect:
        params.append(('no_redirect', 1))
    if no_html:
        params.append(('no_html', 1))
    if skip_disambig:
        params.append(('skip_disambig', 1))

    return '/?' + urlencode(params)


def query(query_string, secure=False, container='namedtuple', verbose=False,
          user_agent=api.USER_AGENT, no_redirect=False, no_html=False,
          skip_disambig=False):
    """
    Generates and sends a query to DuckDuckGo API.

    Args:
        query_string: Query to be passed to DuckDuckGo API.
        secure: Use secure SSL/TLS connection. Default - False.
            Syntactic sugar is secure_query function which is passed the same
            parameters.
        container: Indicates how dict-like objects are serialized. There are
           two possible options: namedtuple and dict. If 'namedtuple' is passed
           the objects will be serialized to namedtuple instance of certain
           class. If 'dict' is passed the objects won't be deserialized.
           Default value: 'namedtuple'.
        verbose: Don't raise any exception if error occurs.
            Default value: False.
        user_agent: User-Agent header of HTTP requests to DuckDuckGo API.
            Default value: 'duckduckpy 0.2'
        no_redirect: Skip HTTP redirects (for !bang commands).
            Default value: False.
        no_html: Remove HTML from text, e.g. bold and italics.
            Default value: False.
        skip_disambig: Skip disambiguation (D) Type. Default value: False.

    Raises:
        DuckDuckDeserializeError: JSON serialization failed.
        DuckDuckConnectionError: Something went wrong with client operation.
        DuckDuckArgumentError: Passed argument is wrong.

    Returns:
        Container depends on container parameter. Each field in the response is
        converted to the so-called snake case.

    Usage:
        >>> import duckduckpy
        >>># Namedtuple is used as a container:
        >>> response = duckduckpy.query('Python')
        >>> response
        Response(redirect=u'', definition=u'', image_width=0, ...}
        >>> type(response)
        <class 'duckduckpy.api.Response'>
        >>> response.related_topics[0]
        Result(first_url=u'https://duckduckgo.com/Python', text=...)
        >>> type(response.related_topics[0])
        <class 'duckduckpy.api.Result'>

        >>># Dict is used as a container:
        >>> response = duckduckpy.query('Python', container='dict')
        >>> type(response)
        <type 'dict'>
        >>> response
        {u'abstract': u'', u'results': [], u'image_is_logo': 0, ...}
        >>> type(response['related_topics'][0])
        <type 'dict'>
        >>> response['related_topics'][0]
        {u'first_url': u'https://duckduckgo.com/Python', u'text': ...}
    """
    if container not in Hook.containers:
        raise exc.DuckDuckArgumentError(
            "Argument 'container' must be one of the values: "
            "{0}".format(', '.join(Hook.containers)))

    headers = {"User-Agent": user_agent}
    url = url_assembler(
        query_string,
        no_redirect=no_redirect,
        no_html=no_html,
        skip_disambig=skip_disambig)

    if secure:
        conn = http_client.HTTPSConnection(api.SERVER_HOST)
    else:
        conn = http_client.HTTPConnection(api.SERVER_HOST)

    try:
        conn.request("GET", url, "", headers)
        resp = conn.getresponse()
        data = decoder(resp.read())
    except socket.gaierror as e:
        raise exc.DuckDuckConnectionError(e.strerror)
    finally:
        conn.close()

    hook = Hook(container, verbose=verbose)
    try:
        obj = json.loads(data, object_hook=hook)
    except ValueError:
        raise exc.DuckDuckDeserializeError(
            "Unable to deserialize response to an object")

    return obj


secure_query = functools.partial(query, secure=True)
