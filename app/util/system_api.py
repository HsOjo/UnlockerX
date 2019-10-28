import re

from app import common
from app.util import object_convert
from app.util.log import Log

_cg_session_info = None


def open_url(url, new=False, wait=False, bundle: str = None):
    args = ['/usr/bin/open']
    if new:
        args.append('-n')
    if wait:
        args.append('-W')
    if bundle:
        args.append('-b')
        args.append(bundle)

    args.append(url)
    return common.execute(args)


def open_preference(name, **kwargs):
    open_url('/System/Library/PreferencePanes/%s.prefPane' % name, bundle='com.apple.systempreferences', **kwargs)


def check_admin(username=None):
    args = ['/usr/bin/groups']
    if username is not None:
        args.append(username)

    content = common.execute_get_out(args)
    groups = content.split(' ')

    return 'admin' in groups


def sudo(command: str, password: str, timeout=None):
    stat, out, err = common.execute('/usr/bin/sudo -S %s' % (command), '%s\n' % password, timeout, shell=True)
    Log.append(sudo, 'sudo', locals())
    return stat, out, err


def get_system_version():
    content = common.execute_get_out(['/usr/sbin/system_profiler', 'SPSoftwareDataType'])
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
    global _cg_session_info
    if _cg_session_info is None:
        import Quartz
        _cg_session_info = getattr(Quartz, 'CGSessionCopyCurrentDictionary')
    return _cg_session_info()


def sleep(display_only=False):
    common.execute(['/usr/bin/pmset', 'displaysleepnow' if display_only else 'sleepnow'])


def check_lid():
    content = common.execute_get_out(['/usr/sbin/ioreg', '-c', 'IOPMrootDomain', '-d', '4'])

    reg = re.compile(r'"AppleClamshellState" = (\S+)')
    result = common.reg_find_one(reg, content, None)

    if result == 'Yes':
        return True
    elif result == 'No':
        return False
    else:
        return None


def get_hid_idle_time():
    content = common.execute_get_out(['/usr/sbin/ioreg', '-c', 'IOHIDSystem', '-d', '4'])

    reg = re.compile(r'"HIDIdleTime" = (\d+)')
    result = common.reg_find_one(reg, content, None)

    return int(result) / 1000000000


def check_display_sleep():
    content = common.execute_get_out(['/usr/sbin/ioreg', '-n', 'AppleBacklightDisplay', '-d', '9'])

    reg = re.compile(r'"dsyp"={"min"=(\d+),"max"=(\d+),"value"=(\d+)}')
    [min_, max_, value] = common.reg_find_one(reg, content, None)

    return min_ == value
