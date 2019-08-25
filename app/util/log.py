import time
from io import StringIO
from threading import Lock

from app.util import io_helper, object_convert

io_log = StringIO()
io_err = StringIO()
lock_log = Lock()


def extract_log():
    with lock_log:
        log = io_helper.read_all(io_log, '')
    return log


def extract_err():
    err = io_helper.read_all(io_err, '')
    return err


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

    with lock_log:
        print('[%s] %s %s\n\t' % (tag, time.ctime(), source), *log_items)
