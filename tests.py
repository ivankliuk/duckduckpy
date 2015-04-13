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
from duckduckpy.core import url_assembler
import duckduckpy.exception as exc
from duckduckpy.utils import camel_to_snake_case


class TestHook(unittest.TestCase):
    def test_non_existent_hook(self):
        self.assertTrue(Hook(1) is None)

    def test_non_existent_hook_verbose(self):
        self.assertRaises(exc.DuckDuckDeserializeError, Hook, 1, verbose=True)

    def test_hook_instance_returned(self):
        hook = Hook(Hook.containers[0])
        self.assertTrue(isinstance(hook, Hook))

    def test_containers_exist(self):
        self.assertTrue(isinstance(Hook.containers, Iterable))
        self.assertTrue(Hook.containers > 0)


class TestHookDictSerializer(unittest.TestCase):
    def setUp(self):
        self.hook = Hook('dict')
        self.assertEqual(self.hook._container, 'dict')

    def test_deserialize_icon(self):
        obj = {'URL': 'www.some.url.com', 'Width': 10, 'Height': 10}
        expected = {'url': 'www.some.url.com', 'width': 10, 'height': 10}
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_result(self):
        obj = {
            'FirstURL': 'www.test.url.com',
            'Icon': 'icon',
            'Result': 20,
            'Text': 'Example of a text'}
        expected = {
            'first_url': 'www.test.url.com',
            'icon': 'icon',
            'result': 20,
            'text': 'Example of a text'}
        actual_dict = self.hook(obj)
        self.assertEqual(actual_dict, expected)

    def test_deserialize_content(self):
        obj = {
            'data_type': 'test_type',
            'label': 'test_label',
            'sort_order': 'order',
            'value': False,
            'wiki_order': 0}
        expected = {
            'data_type': 'test_type',
            'label': 'test_label',
            'sort_order': 'order',
            'value': False,
            'wiki_order': 0}
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_meta(self):
        obj = {'data_type': 'test_type', 'label': True, 'value': 10}
        expected = {'data_type': 'test_type', 'label': True, 'value': 10}
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_infobox(self):
        obj = {'content': 'test content', 'meta': True}
        expected = {'content': 'test content', 'meta': True}
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_response(self):
        obj = {
            'Redirect': 'YES',
            'Definition': 'def',
            'ImageWidth': 20,
            'Infobox': True,
            'RelatedTopics': ['Topics', 'list'],
            'ImageHeight': 45,
            'Heading': 'HEADING',
            'Answer': 'answer',
            'AbstractText': 'test text',
            'Type': 'yes',
            'ImageIsLogo': 'logo',
            'DefinitionSource': 'test source',
            'AbstractURL': 'http://test.abstract.url.com',
            'Abstract': True,
            'DefinitionURL': 'http://test.definition.url.com',
            'Results': [True, 'results', 'list'],
            'Entity': 'test entity',
            'AnswerType': 'True answer',
            'AbstractSource': 'test abstract source',
            'Image': 'test image'}
        expected = {
            'redirect': 'YES',
            'definition': 'def',
            'image_width': 20,
            'infobox': True,
            'related_topics': ['Topics', 'list'],
            'image_height': 45,
            'heading': 'HEADING',
            'answer': 'answer',
            'abstract_text': 'test text',
            'type': 'yes',
            'image_is_logo': 'logo',
            'definition_source': 'test source',
            'abstract_url': 'http://test.abstract.url.com',
            'abstract': True,
            'definition_url': 'http://test.definition.url.com',
            'results': [True, 'results', 'list'],
            'entity': 'test entity',
            'answer_type': 'True answer',
            'abstract_source': 'test abstract source',
            'image': 'test image'}
        actual = self.hook(obj)
        self.assertEqual(actual, expected)


class TestHookNamedTupleSerializer(unittest.TestCase):
    def setUp(self):
        self.hook = Hook('namedtuple')
        self.assertEqual(self.hook._container, 'namedtuple')

    def test_deserialize_icon(self):
        obj = {'URL': 'www.some.url.com', 'Width': 10, 'Height': 10}
        expected_dict = {'url': 'www.some.url.com', 'width': 10, 'height': 10}
        expected = api.Icon(**expected_dict)
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_result(self):
        obj = {
            'FirstURL': 'www.test.url.com',
            'Icon': 'icon',
            'Result': 20,
            'Text': 'Example of a text'}
        expected_dict = {
            'first_url': 'www.test.url.com',
            'icon': 'icon',
            'result': 20,
            'text': 'Example of a text'}
        expected = api.Result(**expected_dict)
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_content(self):
        obj = {
            'data_type': 'test_type',
            'label': 'test_label',
            'sort_order': 'order',
            'value': False,
            'wiki_order': 0}
        expected_dict = {
            'data_type': 'test_type',
            'label': 'test_label',
            'sort_order': 'order',
            'value': False,
            'wiki_order': 0}
        expected = api.Content(**expected_dict)
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_meta(self):
        obj = {'data_type': 'test_type', 'label': True, 'value': 10}
        expected_dict = {'data_type': 'test_type', 'label': True, 'value': 10}
        expected = api.Meta(**expected_dict)
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_infobox(self):
        obj = {'content': 'test content', 'meta': True}
        expected_dict = {'content': 'test content', 'meta': True}
        expected = api.Infobox(**expected_dict)
        actual = self.hook(obj)
        self.assertEqual(actual, expected)

    def test_deserialize_response(self):
        obj = {
            'Redirect': 'YES',
            'Definition': 'def',
            'ImageWidth': 20,
            'Infobox': True,
            'RelatedTopics': ['Topics', 'list'],
            'ImageHeight': 45,
            'Heading': 'HEADING',
            'Answer': 'answer',
            'AbstractText': 'test text',
            'Type': 'yes',
            'ImageIsLogo': 'logo',
            'DefinitionSource': 'test source',
            'AbstractURL': 'http://test.abstract.url.com',
            'Abstract': True,
            'DefinitionURL': 'http://test.definition.url.com',
            'Results': [True, 'results', 'list'],
            'Entity': 'test entity',
            'AnswerType': 'True answer',
            'AbstractSource': 'test abstract source',
            'Image': 'test image'}
        expected_dict = {
            'redirect': 'YES',
            'definition': 'def',
            'image_width': 20,
            'infobox': True,
            'related_topics': ['Topics', 'list'],
            'image_height': 45,
            'heading': 'HEADING',
            'answer': 'answer',
            'abstract_text': 'test text',
            'type': 'yes',
            'image_is_logo': 'logo',
            'definition_source': 'test source',
            'abstract_url': 'http://test.abstract.url.com',
            'abstract': True,
            'definition_url': 'http://test.definition.url.com',
            'results': [True, 'results', 'list'],
            'entity': 'test entity',
            'answer_type': 'True answer',
            'abstract_source': 'test abstract source',
            'image': 'test image'}
        expected = api.Response(**expected_dict)
        actual = self.hook(obj)
        self.assertEqual(actual, expected)


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
