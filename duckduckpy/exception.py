class DuckDuckException(Exception):
    """Base exception class
    """
    pass


class DuckDuckDeserializeError(DuckDuckException):
    """JSON serialization exception
    """
    pass


class DuckDuckConnectionError(DuckDuckException):
    """A wrapper around httplib exceptions. Raised when something went wrong
    with httplib operation.
    """
    pass


class DuckDuckArgumentError(DuckDuckException):
    """Indicates that argument is wrong
    """
    pass
