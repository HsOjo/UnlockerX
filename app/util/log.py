import os
import sys
import time
from io import StringIO
from threading import Lock

from app.res.const import Const
from app.util import io_helper, object_convert


class Log:
    io_log = StringIO()
    io_err = StringIO()
    replaces = {}
    lock_log = Lock()

    @staticmethod
    def init_app():
        log_dir = os.path.expanduser('~/Library/Logs/')

        path_log = '%s/%s.log' % (log_dir, Const.app_name)
        path_err = '%s/%s.err' % (log_dir, Const.app_name)

        Log.io_log = open(path_log, 'w+')
        Log.io_err = open(path_err, 'w+')

        # redirect stdout and stderr.
        sys.stdout = Log.io_log
        sys.stderr = Log.io_err

    @staticmethod
    def set_replaces(replaces: dict):
        Log.replaces = replaces

    @staticmethod
    def extract_log():
        with Log.lock_log:
            log = io_helper.read_all(Log.io_log, '')
        return log

    @staticmethod
    def extract_err():
        err = io_helper.read_all(Log.io_err, '')
        return err

    @staticmethod
    def append(src, tag='Info', *args):
        log_items = []
        for i in args:
            if isinstance(i, list) or isinstance(i, dict):
                log_items.append(object_convert.to_json(i))
            elif isinstance(i, tuple) or isinstance(i, set):
                log_items.append(object_convert.to_json(list(i)))
            elif isinstance(i, int) or isinstance(i, float) or isinstance(i, str) or isinstance(i, bool) or i is None:
                log_items.append(i)
            else:
                log_items.append(i)
                log_items.append(object_convert.to_json(object_convert.object_to_dict(i)))

        if isinstance(src, str):
            source = src
        else:
            source = src.__name__

        items_str = []
        for item in log_items:
            item_str = str(item)
            if len(Log.replaces) > 0:
                for k, v in Log.replaces.items():
                    if k is not None:
                        item_str = item_str.replace(k, v)

            items_str.append(item_str)

        items_str = ' '.join(items_str)

        with Log.lock_log:
            print('[%s] %s %s\n\t' % (tag, time.ctime(), source), items_str)
            Log.io_log.flush()
