import re

from app import common
from app.util.apple_script import AppleScript, ObjectConvertor


def run_as_admin(cmd, pwd, user='', timeout=None):
    cmd = ObjectConvertor.to_object(cmd)
    pwd = ObjectConvertor.to_object(pwd)

    [stat, out, err] = AppleScript.exec(
        'do shell script %s %spassword %s with administrator privileges' % (
            cmd, (('user name %s ' % ObjectConvertor.to_object(user)) if user != '' else ''), pwd), timeout)
    return stat, out, err


def dialog_input(title, description, default='', hidden=False):
    title = ObjectConvertor.to_object(title)
    description = ObjectConvertor.to_object(description)
    default = ObjectConvertor.to_object(default)

    [stat, out, err] = AppleScript.exec(
        'display dialog %s with title %s default answer %s hidden answer %s' %
        (description, title, default, hidden))

    content = None
    if out != '':
        reg = re.compile('text returned:(.*)')
        [content] = reg.findall(out)

    return content


def dialog_select(title, description, buttons: list, default=None):
    title = ObjectConvertor.to_object(title)
    description = ObjectConvertor.to_object(description)
    if default is None:
        default = len(buttons)
    elif isinstance(default, int):
        default += 1
    else:
        default = ObjectConvertor.to_object(default)

    check = [str(i) for i in buttons]
    buttons = ObjectConvertor.to_object(buttons)

    [stat, out, err] = AppleScript.exec(
        'display dialog %s with title %s buttons %s default button %s' %
        (description, title, buttons, default))

    index = None
    if out != '':
        reg = re.compile('button returned:(.*)')
        content = common.reg_find_one(reg, out, None)
        if content in check:
            index = check.index(content)

    return index


def alert(title='', description=''):
    title = ObjectConvertor.to_object(title)
    description = ObjectConvertor.to_object(description)

    [stat, out, err] = AppleScript.exec(
        'display dialog %s with title %s' % (description, title)
    )

    return stat == 0


def choose_from_list(title, description, items: list, multi=False):
    title = ObjectConvertor.to_object(title)
    description = ObjectConvertor.to_object(description)
    multi = ObjectConvertor.to_object(multi)

    check = [str(i) for i in items]
    items = ObjectConvertor.to_object(items)

    [stat, out, err] = AppleScript.exec(
        'choose from list %s with title %s with prompt %s multiple selections allowed %s' %
        (items, title, description, multi)
    )

    out = out.strip()
    index = None
    if out != '':
        if out in check:
            index = check.index(out)

    return index


def choose_folder(title, multi=False):
    title = ObjectConvertor.to_object(title)
    multi = ObjectConvertor.to_object(multi)

    [stat, out, err] = AppleScript.exec(
        'choose folder with prompt %s multiple selections allowed %s' %
        (title, multi)
    )

    out = out.strip()  # type: str
    folder = None
    if out != '':
        folder = out[out.find(':'):].replace(':', '/')

    return folder


def set_login_startup(name, path, hidden=False):
    prop = {
        'name': name,
        'path': path,
        'hidden': hidden,
    }

    [stat, out, err] = AppleScript.exec(
        'tell application "System Events" to make new login item with properties %s' %
        (ObjectConvertor.to_object(prop))
    )

    if out == 'login item %s' % name:
        return True
    else:
        return False


def screen_save():
    code = '''tell application id "com.apple.ScreenSaver.Engine" to launch'''
    [stat, out, err] = AppleScript.exec(code)
