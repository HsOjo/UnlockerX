import os

from .shell import Shell


class Py2App(Shell):
    def __init__(self):
        super().__init__()
        if self.check():
            self.fix_encoding()
            self.runtime_dir = os.path.abspath(os.getcwd())
            self.app_path = os.path.abspath('%s/../..' % self.runtime_dir)

    @staticmethod
    def check():
        return os.getenv('_PY2APP_LAUNCHED_') is not None
