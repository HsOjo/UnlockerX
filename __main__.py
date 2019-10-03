import sys

from app import Application
from app.util import pyinstaller
from app.util.log import Log

if getattr(sys, 'frozen', False):
    # is run at pyinstaller
    pyinstaller.fix_encoding_in_pyinstaller()
    Log.init_app()

app = Application()

try:
    app.run()
except:
    app.callback_exception()
