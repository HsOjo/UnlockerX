import os
import re

from app import common
from app.util import object_convert


def open_url(url, new=False):
    param = ' -n' if new else ''
    os.system('/usr/bin/open%s "%s"' % (param, url))


def check_admin(username=''):
    content = common.execute_get_out('/usr/bin/groups %s' % username)
    groups = content.split(' ')

    return 'admin' in groups


def sudo(command: str, password: str, timeout=None):
    stat = -1
    out = ''

    try:
        p = common.popen('/usr/bin/sudo -S %s' % (command))
        p.stdin.write(password + '\n')
        p.stdin.close()
        out = p.stdout.read()
        err = p.stderr.read()
        stat = p.wait(timeout)
    except:
        err = common.get_exception()

    return stat, out, err


def get_system_version():
    content = common.execute_get_out('/usr/sbin/system_profiler SPSoftwareDataType')
    result = {}
    reg = re.compile('(.*): (.*)')
    for item in reg.findall(content):
        result[item[0].strip()] = item[1].strip()
    return result


def cgsession_info():
    code = 'import Quartz, json; print(json.dumps(dict(Quartz.CGSessionCopyCurrentDictionary())));'
    [stat, out, err] = common.execute('/usr/bin/python', code)
    content = object_convert.from_json(out)  # type: dict
    return content


def sleep(display_only=False):
    os.system('/usr/bin/pmset %s' % ('displaysleepnow' if display_only else 'sleepnow'))
