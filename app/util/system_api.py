import os
import re

from app import common
from app.util import object_convert, log


def open_url(url, new=False, wait=False, bundle=None):
    param = ''
    param += ' -n' if new else ''
    param += ' -W' if wait else ''
    param += ' -b %s' % bundle if bundle is not None else ''
    os.system('/usr/bin/open%s "%s"' % (param, url))


def open_preference(name, **kwargs):
    open_url('/System/Library/PreferencePanes/%s.prefPane' % name, bundle='com.apple.systempreferences', **kwargs)


def check_admin(username=''):
    content = common.execute_get_out('/usr/bin/groups %s' % username)
    groups = content.split(' ')

    return 'admin' in groups


def sudo(command: str, password: str, timeout=None):
    stat, out, err = common.execute('/usr/bin/sudo -S %s' % (command), '%s\n' % password, timeout)
    log.append(sudo, 'sudo', locals())
    return stat, out, err


def get_system_version():
    content = common.execute_get_out('/usr/sbin/system_profiler SPSoftwareDataType')
    result = {}
    reg = re.compile('(.*): (.*)')
    for item in reg.findall(content):
        result[item[0].strip()] = item[1].strip()
    return result


def cg_session_info_py2():
    code = 'import Quartz, json; print(json.dumps(dict(Quartz.CGSessionCopyCurrentDictionary())));'
    [stat, out, err] = common.execute('/usr/bin/python', code)
    content = object_convert.from_json(out)  # type: dict
    return content


def cg_session_info():
    import Quartz
    return getattr(Quartz, 'CGSessionCopyCurrentDictionary')()


def sleep(display_only=False):
    os.system('/usr/bin/pmset %s' % ('displaysleepnow' if display_only else 'sleepnow'))


def check_lid():
    content = common.execute_get_out('/usr/sbin/ioreg -c IOPMrootDomain -d 4')

    reg = re.compile(r'"AppleClamshellState" = (\S+)')
    result = common.reg_find_one(reg, content, None)

    if result == 'Yes':
        return True
    elif result == 'No':
        return False
    else:
        return None


def get_hid_idle_time():
    content = common.execute_get_out('/usr/sbin/ioreg -c IOHIDSystem -d 4')

    reg = re.compile(r'"HIDIdleTime" = (\d+)')
    result = common.reg_find_one(reg, content, None)

    return int(result) / 1000000000
