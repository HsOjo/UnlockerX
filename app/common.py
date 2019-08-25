import os
import sys
import time
import traceback
from io import StringIO
from subprocess import PIPE, Popen


def popen(cmd, sys_env=True, **kwargs):
    if sys_env and kwargs.get('env') is not None:
        kwargs['env'] = os.environ.copy().update(kwargs['env'])
    return Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, encoding='utf-8', **kwargs)


def execute(cmd, input=None, timeout=None, **kwargs):
    p = popen(cmd, **kwargs)
    if input is not None:
        p.stdin.write(input)
        p.stdin.close()
    out = p.stdout.read()
    err = p.stderr.read()
    stat = p.wait(timeout)
    return stat, out, err


def execute_get_out(cmd, **kwargs):
    [_, out, _] = execute(cmd, **kwargs)
    return out


def get_exception():
    with StringIO() as io:
        traceback.print_exc(file=io)
        io.seek(0)
        content = io.read()

    return content


def reg_find_one(reg, content, default=''):
    res = reg.findall(content)
    if len(res) > 0:
        return res[0]
    else:
        return default


def compare_version(a: str, b: str, ex=False):
    sa = a.split('-')
    sb = b.split('-')

    if ex is False and len(sb) > 1:
        return False
    else:
        return int(sa[0].replace('.', '')) < int(sb[0].replace('.', ''))


def wait_and_check(wait: float, step: float):
    def core(func):
        def _core(*args, **kwargs):
            for i in range(int(wait // step)):
                if not func(*args, **kwargs):
                    return False
                time.sleep(step)
            time.sleep(wait % step)
            return True

        return _core

    return core


def time_count(func):
    def core(*args, **kwargs):
        t = time.time()
        result = func(*args, **kwargs)
        print('%s time usage: %f' % (func.__name__, time.time() - t))
        return result

    return core


def site_package_path():
    sp_paths = [x for x in sys.path if 'site-packages' in x]
    if len(sp_paths) > 0:
        sp_path = sp_paths[0]
    else:
        sp_path = None
    return sp_path


def python_path():
    paths = []
    for x in sys.path:
        path = '%s/../../bin/python' % x
        if 'python' in x and os.path.isdir(x) and os.path.exists(path):
            path = os.path.abspath(path)
            paths.append(path)

    if len(paths) > 0:
        return paths[0]

    return None
