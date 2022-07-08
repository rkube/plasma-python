# -*- coding: utf-8 -*-

class NotDownloadedError(Exception):
    """Raised when a signal is accessed that is not on the file system."""
    pass


class SignalCorruptedError(Exception):
    """Raised when a signal is unusable."""
    pass

class SignalNotFoundError(Exception):
    """Raised when a signal wasn't found"""



# end of file errors.py