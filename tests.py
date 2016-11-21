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


class TestHook(unittest.TestCase):
    def test_non_existent_hook(self):
        self.assertTrue(Hook(1) is None)

    def test_hook_instance_returned(self):
        hook = Hook(Hook.containers[0])
        self.assertTrue(isinstance(hook, Hook))

    def test_containers_exist(self):
        self.assertTrue(isinstance(Hook.containers, Iterable))
        self.assertTrue(Hook.containers > 0)

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
        expected = "/?q=test+query&no_redirect=1&format=json"
        url = url_assembler("test query", no_redirect=True)
        self.assertEqual(url, expected)

    def test_no_html(self):
        expected = "/?q=test+query&no_html=1&format=json"
        url = url_assembler("test query", no_html=True)
        self.assertEqual(url, expected)

    def test_skip_disambig(self):
        expected = "/?q=test+query&skip_disambig=1&format=json"
        url = url_assembler("test query", skip_disambig=True)
        self.assertEqual(url, expected)

    def test_all_options_are_on(self):
        expected = ("/?q=test+query&no_html=1&"
                    "no_redirect=1&skip_disambig=1&format=json")
        url = url_assembler("test query",
                            no_redirect=True, no_html=True, skip_disambig=True)
        self.assertEqual(url, expected)


@mock.patch('httplib.HTTPConnection.request')
class TestQuery(unittest.TestCase):
    origin = """{
   \"DefinitionSource\" : \"\",
   \"Heading\" : \"Python\",
   \"ImageWidth\" : 0,
   \"RelatedTopics\" : [
      {
         \"Result\" : \"<a href=\\"https://duckduckgo.com/Python_(programmin\",
         \"Icon\" : {
            \"URL\" : \"https://duckduckgo.com/i/7eec482b.png\",
            \"Height\" : \"\",
            \"Width\" : \"\"
         },
         \"FirstURL\" : \"https://duckduckgo.com/Python_(programming\",
         \"Text\" : \"Python (programming language)A widely used general\"
      },
      {
         \"Result\" : \"<a href=\\"https://duckduckgo.com/Monty_Python\\">Mo\",
         \"Icon\" : {
            \"URL\" : \"https://duckduckgo.com/i/4eec9e83.jpg\",
            \"Height\" : \"\",
            \"Width\" : \"\"
         },
         \"FirstURL\" : \"https://duckduckgo.com/Monty_Python\",
         \"Text\" : \"Monty PythonA British surreal comedy group who\"
      },
      {
         \"Result\" : \"<a href=\\"https://duckduckgo.com/Colt_Python\\">Co\",
         \"Icon\" : {
            \"URL\" : \"https://duckduckgo.com/i/7e29c05b.jpg\",
            \"Height\" : \"\",
            \"Width\" : \"\"
         },
         \"FirstURL\" : \"https://duckduckgo.com/Colt_Python\",
         \"Text\" : \"Colt PythonA.357 Magnum caliber revolver formerly\"
      }
   ],
   \"Entity\" : \"\",
   \"Type\" : \"D\",
   \"Redirect\" : \"\",
   \"DefinitionURL\" : \"\",
   \"AbstractURL\" : \"https://en.wikipedia.org/wiki/Python\",
   \"Definition\" : \"\",
   \"AbstractSource\" : \"Wikipedia\",
   \"Infobox\" : \"\",
   \"Image\" : \"\",
   \"ImageIsLogo\" : 0,
   \"Abstract\" : \"\",
   \"AbstractText\" : \"\",
   \"AnswerType\" : \"\",
   \"ImageHeight\" : 0,
   \"Results\" : [],
   \"Answer\" : \"\"
}"""
    icon1 = {'height': '',
             'url': 'https://duckduckgo.com/i/7eec482b.png',
             'width': ''}

    icon2 = {'height': '',
             'url': 'https://duckduckgo.com/i/4eec9e83.jpg',
             'width': ''}

    icon3 = {'height': '',
             'url': 'https://duckduckgo.com/i/7e29c05b.jpg',
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

    result3 = {
        'first_url': 'https://duckduckgo.com/Colt_Python',
        'icon': icon3,
        'result': '<a href="https://duckduckgo.com/Colt_Python">Co',
        'text': "Colt PythonA.357 Magnum caliber revolver formerly"}

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
        'infobox': '',
        'redirect': '',
        'related_topics': [result1, result2, result3],
        'results': [],
        'type': 'D'}

    @mock.patch('json.loads')
    @mock.patch('httplib.HTTPConnection')
    def test_http_connection_used(self, conn, *args):
        query('anything', secure=False)
        conn.assert_called_once_with(api.SERVER_HOST)

    @mock.patch('httplib.HTTPConnection.getresponse',
                return_value=StringIO(origin))
    def test_smoke_dict(self, *args):
        resp = query('python', container='dict')
        self.assertEqual(resp, self.response)

    @mock.patch('httplib.HTTPConnection.getresponse',
                return_value=StringIO(origin))
    def test_smoke_namedtuple(self, *args):
        self.result1['icon'] = api.Icon(**self.icon1)
        self.result2['icon'] = api.Icon(**self.icon2)
        self.result3['icon'] = api.Icon(**self.icon3)

        self.response['related_topics'] = [
            api.Result(**self.result1),
            api.Result(**self.result2),
            api.Result(**self.result3)]

        expected = api.Response(**self.response)
        resp = query('python')
        self.assertEqual(resp, expected)

    @mock.patch('httplib.HTTPConnection.getresponse',
                return_value=StringIO("[1, \"x\", true]"))
    def test_json_response_as_list(self, *args):
        res = query('anything!')
        self.assertEqual(res, [1, 'x', True])

    @mock.patch('httplib.HTTPConnection.getresponse',
                return_value=StringIO("Not JSON"))
    def test_not_json_response(self, *args):
        self.assertRaises(exc.DuckDuckDeserializeError, query, 'anything!')


class TestSecureQuery(unittest.TestCase):
    @mock.patch('json.loads')
    @mock.patch('httplib.HTTPSConnection')
    def test_https_connection_used(self, conn, *args):
        query('anything', secure=True)
        conn.assert_called_once_with(api.SERVER_HOST)

    @mock.patch('json.loads')
    @mock.patch('httplib.HTTPSConnection')
    def test_shortcut_https_connection_used(self, conn, *args):
        secure_query('anything', secure=True)
        conn.assert_called_once_with(api.SERVER_HOST)


class TestQueryExceptions(unittest.TestCase):
    @mock.patch('httplib.HTTPConnection.getresponse',
                side_effect=exc.DuckDuckArgumentError)
    def test_argument_error(self, *args):
        self.assertRaises(
            exc.DuckDuckArgumentError, query, '', container='non-existent')

    @mock.patch('httplib.HTTPConnection.getresponse',
                side_effect=socket.gaierror)
    def test_connection_error(self, *args):
        self.assertRaises(exc.DuckDuckConnectionError, query, 'anything!')


if __name__ == '__main__':
    unittest.main()
