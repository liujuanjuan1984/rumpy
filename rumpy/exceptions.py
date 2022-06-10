# -*- coding: utf-8 -*-


class RumException(Exception):
    """Base exception for rumpy"""

    def __init__(self, errcode, errmsg):
        """
        :param errcode: Error code
        :param errmsg: Error message
        """
        self.errcode = errcode
        self.errmsg = errmsg

    def __str__(self):
        s = f"Error code: {self.errcode}, message: {self.errmsg}"
        return s

    def __repr__(self):
        _repr = f"{self.__class__.__name__}({self.errcode}, {self.errmsg})"
        return _repr


class RumClientException(RumException):
    """rumpy client exception class"""

    def __init__(self, errcode, errmsg, client=None, request=None, response=None):
        super().__init__(errcode, errmsg)
        self.client = client
        self.request = request
        self.response = response


class ParamTypeError(RumClientException):
    pass


class ParamValueError(RumClientException):
    pass


class ParamOverflowError(RumClientException):
    pass


class ParamRequiredError(RumClientException):
    pass


class RumChainException(RumException):
    """rumpy chain exception class"""

    def __init__(self, errcode, errmsg, request=None, response=None):
        super().__init__(errcode, errmsg)
        self.request = request
        self.response = response


class APILimitedException(RumClientException):
    """Rum API call limited exception class"""

    pass
