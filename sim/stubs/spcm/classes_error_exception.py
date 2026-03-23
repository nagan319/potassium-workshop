"""Stub for spcm.classes_error_exception."""


class SpcmException(Exception):
    pass


class SpcmError(SpcmException):
    pass


class SpcmTimeout(SpcmException):
    pass
