# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import unittest
from collections import Iterable
from io import StringIO
import mock
import socket

from duckduckpy.core import api
from duckduckpy.core import Hook
from duckduckpy.core import query
from duckduckpy.core import secure_query
from duckduckpy.core import url_assembler
import duckduckpy.exception as exc
from duckduckpy.utils import camel_to_snake_case
from duckduckpy.utils import is_python2


class TestHook(unittest.TestCase):
    def test_non_existent_hook(self):
        self.assertTrue(Hook(1) is None)

    def test_hook_instance_returned(self):
        hook = Hook(Hook.containers[0])
        self.assertTrue(isinstance(hook, Hook))

    def test_containers_exist(self):
        self.assertTrue(isinstance(Hook.containers, Iterable))
        self.assertTrue(len(Hook.containers) > 0)

    def test_no_object_found(self):
        obj = {
            'URL': 'www.test.url.com',
            'SomeThing': 'icon',
            'Result': 20,
            'Text': 'Example of a text'}
        expected = {
            'URL': 'www.test.url.com',
            'SomeThing': 'icon',
            'Result': 20,
            'Text': 'Example of a text'}
        hook = Hook('dict')
        actual_dict = hook(obj)
        self.assertEqual(actual_dict, expected)


class TestHookExceptions(unittest.TestCase):
    def test_non_existent_hook_verbose(self):
        self.assertRaises(exc.DuckDuckDeserializeError, Hook, 1, verbose=True)

    def test_no_object_found_verbose(self):
        obj = {
            'URL': 'www.test.url.com',
            'SomeThing': 'icon',
            'Result': 20,
            'Text': 'Example of a text'}
        hook = Hook('dict', verbose=True)
        self.assertRaises(exc.DuckDuckDeserializeError, hook, obj)


class TestCamelToSnakeCase(unittest.TestCase):
    def assertConverted(self, camel_case_string, snake_case_string):
        self.assertEqual(snake_case_string,
                         camel_to_snake_case(camel_case_string))

    def test_conversion_one_word(self):
        self.assertConverted('Camel', 'camel')

    def test_conversion_two_words(self):
        self.assertConverted('CamelCase', 'camel_case')

    def test_conversion_three_words(self):
        self.assertConverted('CamelCaseToo', 'camel_case_too')

    def test_conversion_three_mixed(self):
        self.assertConverted('CamelCase_Underscore', 'camel_case__underscore')

    def test_conversion_with_numbers(self):
        self.assertConverted('Camel2CaseToo3', 'camel2_case_too3')

    def test_conversion_equal(self):
        self.assertConverted('camel_case', 'camel_case')

    def test_conversion_mixed_case(self):
        self.assertConverted('getHTTPResponseCode', 'get_http_response_code')

    def test_conversion_mixed_case_with_numbers(self):
        self.assertConverted('get2HTTPResponseCode', 'get2_http_response_code')

    def test_conversion_uppercase_one_after_another(self):
        self.assertConverted('HTTPResponseCode', 'http_response_code')


class TestURLAssembler(unittest.TestCase):
    def test_simple(self):
        expected = "/?q=test+query&format=json"
        self.assertEqual(url_assembler("test query"), expected)

    def test_cyrillic(self):
        expected = (
            "/?q=%D0%A1%D0%BB%D0%B0%D0%B2%D0%B0+%D0%"
            "A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D1%96&format=json")
        url = url_assembler('Слава Україні')
        self.assertEqual(url, expected)

    def test_no_redirect(self):
        expected = "/?q=test+query&format=json&no_redirect=1"
        url = url_assembler("test query", no_redirect=True)
        self.assertEqual(url, expected)

    def test_no_html(self):
        expected = "/?q=test+query&format=json&no_html=1"
        url = url_assembler("test query", no_html=True)
        self.assertEqual(url, expected)

    def test_skip_disambig(self):
        expected = "/?q=test+query&format=json&skip_disambig=1"
        url = url_assembler("test query", skip_disambig=True)
        self.assertEqual(url, expected)

    def test_all_options_are_on(self):
        expected = ("/?q=test+query&format=json&no_redirect=1"
                    "&no_html=1&skip_disambig=1")
        url = url_assembler("test query",
                            no_redirect=True, no_html=True, skip_disambig=True)
        self.assertEqual(url, expected)

    def test_language_region(self):
        expected = ("/?q=test+query&format=json&kl=ru-ru")
        url = url_assembler("test query", lang="ru-ru")
        self.assertEqual(url, expected)


@mock.patch('duckduckpy.core.http_client.HTTPConnection.request')
class TestQuery(unittest.TestCase):
    origin = r"""
{
  "Abstract": "",
  "AbstractSource": "Wikipedia",
  "AbstractText": "",
  "AbstractURL": "https://en.wikipedia.org/wiki/Python",
  "Answer": "",
  "AnswerType": "",
  "Definition": "",
  "DefinitionSource": "",
  "DefinitionURL": "",
  "Entity": "",
  "Heading": "Python",
  "Image": "",
  "ImageHeight": 0,
  "ImageIsLogo": 0,
  "ImageWidth": 0,
  "Infobox": {},
  "Redirect": "",
  "RelatedTopics": [
    {
      "FirstURL": "https://duckduckgo.com/Python_(programming",
      "Icon": {
        "Height": "",
        "URL": "https://duckduckgo.com/i/7eec482b.png",
        "Width": ""
      },
      "Result": "<a href=\"https://duckduckgo.com/Python_(programmin",
      "Text": "Python (programming language)A widely used general"
    },
    {
      "FirstURL": "https://duckduckgo.com/Monty_Python",
      "Icon": {
        "Height": "",
        "URL": "https://duckduckgo.com/i/4eec9e83.jpg",
        "Width": ""
      },
      "Result": "<a href=\"https://duckduckgo.com/Monty_Python\">Mo",
      "Text": "Monty PythonA British surreal comedy group who"
    },
    {
      "Name": "Ancient Greece",
      "Topics": [
        {
          "FirstURL": "https://duckduckgo.com/Python_(programming",
          "Icon": {
            "Height": "",
            "URL": "https://duckduckgo.com/i/7eec482b.png",
            "Width": ""
          },
          "Result": "<a href=\"https://duckduckgo.com/Python_(programmin",
          "Text": "Python (programming language)A widely used general"
        },
        {
          "FirstURL": "https://duckduckgo.com/Monty_Python",
          "Icon": {
            "Height": "",
            "URL": "https://duckduckgo.com/i/4eec9e83.jpg",
            "Width": ""
          },
          "Result": "<a href=\"https://duckduckgo.com/Monty_Python\">Mo",
          "Text": "Monty PythonA British surreal comedy group who"
        }
      ]
    }
  ],
  "Results": [],
  "Type": "D",
  "meta": {
    "attribution": null,
    "blockgroup": null,
    "created_date": null,
    "description": "Wikipedia",
    "designer": null,
    "dev_date": null,
    "dev_milestone": "live",
    "developer": [
      {
        "name": "DDG Team",
        "type": "ddg",
        "url": "http://www.duckduckhack.com"
      }
    ],
    "example_query": "nikola tesla",
    "id": "wikipedia_fathead",
    "is_stackexchange": null,
    "js_callback_name": "wikipedia",
    "live_date": null,
    "maintainer": {
      "github": "duckduckgo"
    },
    "name": "Wikipedia",
    "perl_module": "DDG::Fathead::Wikipedia",
    "producer": null,
    "production_state": "online",
    "repo": "fathead",
    "signal_from": "wikipedia_fathead",
    "src_domain": "en.wikipedia.org",
    "src_id": 1,
    "src_name": "Wikipedia",
    "src_options": {
      "directory": "",
      "is_fanon": 0,
      "is_mediawiki": 1,
      "is_wikipedia": 1,
      "language": "en",
      "min_abstract_length": "20",
      "skip_abstract": 0,
      "skip_abstract_paren": 0,
      "skip_end": "0",
      "skip_icon": 0,
      "skip_image_name": 0,
      "skip_qr": "",
      "source_skip": "",
      "src_info": ""
    },
    "src_url": null,
    "status": "live",
    "tab": "About",
    "topic": [
      "productivity"
    ],
    "unsafe": 0
  }
}"""
    icon1 = {'height': '',
             'url': 'https://duckduckgo.com/i/7eec482b.png',
             'width': ''}

    icon2 = {'height': '',
             'url': 'https://duckduckgo.com/i/4eec9e83.jpg',
             'width': ''}

    result1 = {
        'first_url': 'https://duckduckgo.com/Python_(programming',
        'icon': icon1,
        'result': '<a href="https://duckduckgo.com/Python_(programmin',
        'text': 'Python (programming language)A widely used general'}

    result2 = {
        'first_url': 'https://duckduckgo.com/Monty_Python',
        'icon': icon2,
        'result': '<a href="https://duckduckgo.com/Monty_Python">Mo',
        'text': "Monty PythonA British surreal comedy group who"}

    related_topic = {
        'name': "Ancient Greece",
        'topics': []
    }

    meta = {
        "attribution": None,
        "blockgroup": None,
        "created_date": None,
        "description": "Wikipedia",
        "designer": None,
        "dev_date": None,
        "dev_milestone": "live",
        "developer": [
            {
                "name": "DDG Team",
                "type": "ddg",
                "url": "http://www.duckduckhack.com"
            }
        ],
        "example_query": "nikola tesla",
        "id": "wikipedia_fathead",
        "is_stackexchange": None,
        "js_callback_name": "wikipedia",
        "live_date": None,
        "maintainer": {
            "github": "duckduckgo"
        },
        "name": "Wikipedia",
        "perl_module": "DDG::Fathead::Wikipedia",
        "producer": None,
        "production_state": "online",
        "repo": "fathead",
        "signal_from": "wikipedia_fathead",
        "src_domain": "en.wikipedia.org",
        "src_id": 1,
        "src_name": "Wikipedia",
        "src_options": {
            "directory": "",
            "is_fanon": 0,
            "is_mediawiki": 1,
            "is_wikipedia": 1,
            "language": "en",
            "min_abstract_length": "20",
            "skip_abstract": 0,
            "skip_abstract_paren": 0,
            "skip_end": "0",
            "skip_icon": 0,
            "skip_image_name": 0,
            "skip_qr": "",
            "source_skip": "",
            "src_info": ""
        },
        "src_url": None,
        "status": "live",
        "tab": "About",
        "topic": [
            "productivity"
        ],
        "unsafe": 0
    }
    response = {
        'abstract': '',
        'abstract_source': 'Wikipedia',
        'abstract_text': '',
        'abstract_url': 'https://en.wikipedia.org/wiki/Python',
        'answer': '',
        'answer_type': '',
        'definition': '',
        'definition_source': '',
        'definition_url': '',
        'entity': '',
        'heading': 'Python',
        'image': '',
        'image_height': 0,
        'image_is_logo': 0,
        'image_width': 0,
        'infobox': {},
        'redirect': '',
        'related_topics': [],
        'results': [],
        'type': 'D',
        'meta': meta}

    @mock.patch('json.loads')
    @mock.patch('duckduckpy.core.http_client.HTTPConnection')
    def test_http_connection_used(self, conn, *args):
        query('anything', secure=False)
        conn.assert_called_once_with(api.SERVER_HOST)

    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                return_value=StringIO(origin))
    def test_smoke_dict(self, *args):
        self.related_topic['topics'] = [self.result1, self.result2]
        self.response['related_topics'] = [
            self.result1, self.result2, self.related_topic]
        resp = query('python', container='dict')
        self.assertTrue(resp == self.response)

    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                return_value=StringIO(origin))
    def test_smoke_namedtuple(self, *args):
        self.result1['icon'] = api.Icon(**self.icon1)
        self.result2['icon'] = api.Icon(**self.icon2)

        self.related_topic['topics'] = [
            api.Result(**self.result1),
            api.Result(**self.result2)]

        self.response['related_topics'] = [
            api.Result(**self.result1),
            api.Result(**self.result2),
            api.RelatedTopic(**self.related_topic)]

        expected = api.Response(**self.response)
        resp = query('python')
        self.assertEqual(resp, expected)

    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                return_value=mock.Mock(read=lambda: b"{}"))
    def test_python3_utf8_decode(self, *args):
        # Not relevant to Python 2.
        if not is_python2():
            query('python', container='dict')

    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                return_value=StringIO("[1, \"x\", true]"))
    def test_json_response_as_list(self, *args):
        res = query('anything!')
        self.assertEqual(res, [1, 'x', True])

    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                return_value=StringIO("Not JSON"))
    def test_not_json_response(self, *args):
        self.assertRaises(exc.DuckDuckDeserializeError, query, 'anything!')


class TestSecureQuery(unittest.TestCase):
    @mock.patch('json.loads')
    @mock.patch('duckduckpy.core.http_client.HTTPSConnection')
    def test_https_connection_used(self, conn, *args):
        query('anything', secure=True)
        conn.assert_called_once_with(api.SERVER_HOST)

    @mock.patch('json.loads')
    @mock.patch('duckduckpy.core.http_client.HTTPSConnection')
    def test_shortcut_https_connection_used(self, conn, *args):
        secure_query('anything', secure=True)
        conn.assert_called_once_with(api.SERVER_HOST)


class TestQueryExceptions(unittest.TestCase):
    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                side_effect=exc.DuckDuckArgumentError)
    def test_argument_error(self, *args):
        self.assertRaises(
            exc.DuckDuckArgumentError, query, '', container='non-existent')

    @mock.patch('duckduckpy.core.http_client.HTTPConnection.getresponse',
                side_effect=socket.gaierror)
    def test_connection_error(self, *args):
        self.assertRaises(exc.DuckDuckConnectionError, query, 'anything!')


if __name__ == '__main__':
    unittest.main()
