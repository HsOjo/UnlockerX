import os
import sys

from .shell import Shell


class PyInstaller(Shell):
    def __init__(self):
        super().__init__()
        if self.check():
            self.fix_encoding()
            self.runtime_dir = os.path.abspath(getattr(sys, '_MEIPASS', '.'))
            if getattr(sys, 'frozen', False):
                self.app_path = os.path.abspath('%s/../../..' % sys.executable)

    @staticmethod
    def check():
        return getattr(sys, '_MEIPASS', None) is not None
