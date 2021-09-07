

class HLTVApiException(Exception):
    """Base class for exception caused in this module."""
    pass

class HLTVRequestException(HLTVApiException):
    """Exception raised for when a request fails. """

    def __init__(self, message, status_code, response):
        self.message = message
        self.status_code = status_code
        self.response = response

class HLTVInvalidInputException(HLTVApiException):
    """Exception when user gives an invalid input"""

    def __init__(self, message, expected):
        self.message = message
        self.expected = expected
