import sys
from subprocess import Popen


class Shell:
    def __init__(self):
        self.runtime_dir = '.'
        self.app_path = None

    @staticmethod
    def check():
        return False

    def get_app_path(self):
        return self.app_path

    def get_runtime_dir(self):
        return self.runtime_dir

    @staticmethod
    def fix_encoding():
        encoding = sys.getdefaultencoding()
        _init = Popen.__init__

        def init(*args, **kwargs):
            kwargs['encoding'] = kwargs.get('encoding', encoding)
            return _init(*args, **kwargs)

        Popen.__init__ = init

        __open = open

        def _open(*args, **kwargs):
            if len(args) >= 2:
                mode = args[1]
            else:
                mode = kwargs.get('mode')

            if isinstance(mode, str) and 'b' not in mode:
                kwargs['encoding'] = kwargs.get('encoding', encoding)
            return __open(*args, **kwargs)

        __builtins__['open'] = _open
