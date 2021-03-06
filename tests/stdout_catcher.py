from cStringIO import StringIO
import sys


class StdoutCatcher(object):
    """

        Example

            with StdoutCatcher as catcher:
                print "hello"

            self.assertEqual("hello", catcher.stdout)
        Can be used in the with context to capture stdout.
    """
    def __init__(self):
        self.output = ""
        self._stringio = None

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.output = self._stringio.getvalue()
        sys.stdout = self._stdout
