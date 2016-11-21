DuckDuckPy
==========

|package| |travis-ci| |coveralls|

`DuckDuckPy <https://github.com/ivankliuk/duckduckpy>`_ is a Python
library for querying `DuckDuckGo API <https://api.duckduckgo.com/api>`_ and
render results either to Python dictionary or namedtuple.

Features
--------

* Uses standard library only
* Works on Python 2.6 and 2.7
* Unit test coverage 100%
* SSL and unicode support
* Licensed under MIT license

Installation
------------

You can install DuckDuckPy either via the `Python Package Index (PyPI) <http://pypi.python.org/pypi>`_ or
from source.

To install using ``pip``:

.. code:: bash

    $ pip install duckduckpy

To install using ``easy_install``:

.. code:: bash

    $ easy_install duckduckpy

To install from sources you can download the latest version of DuckDuckPy
either from `PyPI <http://pypi.python.org/pypi/duckduckpy/0.1>`_ or
`GitHub <https://github.com/ivankliuk/duckduckpy/tarball/0.1>`_, extract archive contents and
run following command from the source directory:

.. code:: bash

    $ python setup.py install

Latest upstream version can be installed directly from the git repository:

.. code:: bash

    $ pip install git+https://github.com/ivankliuk/duckduckpy.git

API description
---------------

.. code-block:: python

    query(query_string, secure=False, container=u'namedtuple', verbose=False,
          user_agent=u'duckduckpy 0.1', no_redirect=False, no_html=False,
          skip_disambig=False)

Generates and sends a query to DuckDuckGo API.

**Arguments:**

+---------------+-------------------------------------------------------------+
| query_string  | Query to be passed to DuckDuckGo API.                       |
+---------------+-------------------------------------------------------------+
| secure        | Use secure SSL/TLS connection. Default - False.             |
|               | Syntactic sugar is secure_query function which is passed    |
|               | the same parameters.                                        |
+---------------+-------------------------------------------------------------+
| container     | Indicates how dict-like objects are serialized. There are   |
|               | two possible options: namedtuple and dict. If 'namedtuple'  |
|               | is passed the objects will be serialized to namedtuple      |
|               | instance of certain class. If 'dict' is passed the objects  |
|               | won't be deserialized. Default value: 'namedtuple'.         |
+---------------+-------------------------------------------------------------+
| verbose       | Don't raise any exception if error occurs.                  |
|               | Default value: False.                                       |
+---------------+-------------------------------------------------------------+
| user_agent    | User-Agent header of HTTP requests to DuckDuckGo API.       |
|               | Default value: 'duckduckpy 0.1'                             |
+---------------+-------------------------------------------------------------+
| no_redirect   | Skip HTTP redirects (for !bang commands).                   |
|               | Default value: False.                                       |
+---------------+-------------------------------------------------------------+
| no_html       | Remove HTML from text, e.g. bold and italics.               |
|               | Default value: False.                                       |
+---------------+-------------------------------------------------------------+
| skip_disambig | Skip disambiguation (D) Type. Default value: False.         |
+---------------+-------------------------------------------------------------+

**Raises:**

+--------------------------+--------------------------------------------------+
| DuckDuckDeserializeError | JSON serialization failed.                       |
+--------------------------+--------------------------------------------------+
| DuckDuckConnectionError  | Something went wrong with httplib operation.     |
+--------------------------+--------------------------------------------------+
| DuckDuckArgumentError    | Passed argument is wrong.                        |
+--------------------------+--------------------------------------------------+

**Returns:**

Container depends on container parameter. Each field in the response is
converted to the so-called snake case.

Usage
-----

.. code-block:: python

    >>> from duckduckpy import query
    >>> response = query('Python') # namedtuple is used as a container
    >>> response
    Response(redirect=u'', definition=u'', image_width=0, ...}
    >>> type(response)
    <class 'duckduckpy.api.Response'>
    >>> response.related_topics[0]
    Result(first_url=u'https://duckduckgo.com/Python', text=...)
    >>> type(response.related_topics[0])
    <class 'duckduckpy.api.Result'>

    >>> response = query('Python', container='dict') # dict as the container
    >>> type(response)
    <type 'dict'>
    >>> response
    {u'abstract': u'', u'results': [], u'image_is_logo': 0, ...}
    >>> type(response['related_topics'][0])
    <type 'dict'>
    >>> response['related_topics'][0]
    {u'first_url': u'https://duckduckgo.com/Python', u'text': ...}

TODO
----

* Python 3 support
* SSL certificate checking

.. |package| image:: https://badge.fury.io/py/duckduckpy.svg
    :target: http://badge.fury.io/py/duckduckpy
    :alt: PyPI package
.. |travis-ci| image:: https://travis-ci.org/ivankliuk/duckduckpy.svg?branch=master
    :target: https://travis-ci.org/ivankliuk/duckduckpy
    :alt: CI Status
.. |coveralls| image:: https://coveralls.io/repos/ivankliuk/duckduckpy/badge.svg?branch=master
    :target: https://coveralls.io/r/ivankliuk/duckduckpy?branch=master
    :alt: Coverage
