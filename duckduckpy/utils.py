import re


_1 = re.compile(r'(.)([A-Z][a-z]+)')
_2 = re.compile('([a-z0-9])([A-Z])')


def camel_to_snake_case(string):
    """Converts 'string' presented in camel case to snake case.

    e.g.: CamelCase => snake_case
    """
    s = _1.sub(r'\1_\2', string)
    return _2.sub(r'\1_\2', s).lower()
