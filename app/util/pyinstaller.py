import os
import sys
from subprocess import Popen


def get_application_info():
    name = None
    path = None
    if getattr(sys, 'frozen', False):
        name = os.path.basename(sys.executable)
        path = os.path.abspath('%s/../../..' % sys.executable)

    return name, path


def get_runtime_dir():
    return getattr(sys, '_MEIPASS', '.')


def fix_encoding_in_pyinstaller():
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
