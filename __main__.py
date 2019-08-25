import os
import sys

from app import Application, common
from app.res.const import Const
from app.util import log, pyinstaller

if getattr(sys, 'frozen', False):
    # is run at pyinstaller
    pyinstaller.fix_encoding_in_pyinstaller()

    log_dir = os.path.expanduser('~/Library/Logs/')

    path_log = '%s/%s.log' % (log_dir, Const.app_name)
    path_err = '%s/%s.err' % (log_dir, Const.app_name)

    common.io_log = open(path_log, 'w+')
    common.io_err = open(path_err, 'w+')

    # redirect stdout and stderr.
    sys.stdout = log.io_log
    sys.stderr = log.io_err

app = Application()

try:
    app.run()
except:
    app.callback_exception()
