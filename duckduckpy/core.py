# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import functools
import httplib
import json
import socket
import urllib

from . import api
from . import exception as exc
from .utils import camel_to_snake_case


class Hook(object):
    """A hook for dict-objects serialization"""
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
        for key in self.dict_object:
            self.dict_object[
                camel_to_snake_case(key)] = self.dict_object.pop(key)

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
        if keys == api.ICON_KEYS:
            return self.serialize('Icon')
        elif keys == api.RESULT_KEYS:
            return self.serialize('Result')
        elif keys == api.CONTENT_KEYS:
            return self.serialize('Content')
        elif keys == api.META_KEYS:
            return self.serialize('Meta')
        elif keys == api.INFOBOX_KEYS:
            return self.serialize('Infobox')
        elif keys == api.RESPONSE_KEYS:
            return self.serialize('Response')

        if not self._verbose:
            return dict_object
        raise exc.DuckDuckDeserializeError(
            "Unable to deserialize dict to an object")


def url_assembler(query_string, no_redirect=0, no_html=0, skip_disambig=0):
    """Assembler of parameters for building request query

    :param query_string:
    :param no_redirect:
    :param no_html:
    :param skip_disambig:
    :return:
    """

    params = {'q': query_string.encode("utf-8"), 'format': 'json'}

    if no_redirect:
        params.update({'no_redirect': 1})
    if no_html:
        params.update({'no_html': 1})
    if skip_disambig:
        params.update({'skip_disambig': 1})

    return '/?' + urllib.urlencode(params)


def query(query_string, secure=False, container='namedtuple', verbose=False,
          user_agent=api.USER_AGENT, no_redirect=False, no_html=False,
          skip_disambig=False):
    """

    :param query_string:
    :param secure:
    :param container:
    :param verbose:
    :param user_agent:
    :param no_redirect:
    :param no_html:
    :param skip_disambig:
    :return:
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
        conn = httplib.HTTPSConnection(api.SERVER_HOST)
    else:
        conn = httplib.HTTPConnection(api.SERVER_HOST)

    try:
        conn.request("GET", url, "", headers)
        resp = conn.getresponse()
        data = resp.read()
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
