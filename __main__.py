import sys

from app import Application
from app.util import log, pyinstaller

if getattr(sys, 'frozen', False):
    # is run at pyinstaller
    pyinstaller.fix_encoding_in_pyinstaller()
    log.init_app_log()

app = Application()

try:
    app.run()
except:
    app.callback_exception()
