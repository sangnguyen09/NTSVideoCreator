import io
from collections import UserString
from contextlib import redirect_stdout

class CaptureOutputStderr(UserString, str, redirect_stdout):
    '''
    Captures stdout (e.g., from ``print()``) as a variable.

    Based on ``contextlib.redirect_stdout``, but saves the user the trouble of
    defining and reading from an IO stream. Useful for testing the output of functions
    that are supposed to print certain output.
    '''

    def __init__(self, seq='', *args, **kwargs):
        self._io = io.StringIO()
        UserString.__init__(self, seq=seq, *args, **kwargs)
        redirect_stdout.__init__(self, self._io)
        return

    def __enter__(self, *args, **kwargs):
        redirect_stdout.__enter__(self, *args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self.data += self._io.getvalue()
        redirect_stdout.__exit__(self, *args, **kwargs)
        return

    def start(self):
        self.__enter__()
        return self

    def stop(self):
        self.__exit__(None, None, None)
        return