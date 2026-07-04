from __future__ import annotations

import getpass
from typing import Optional

from app.platform import proc
from app.res.const import Const

_SERVICE = Const.keychain_service


def _account() -> str:
    return getpass.getuser()


def has_password() -> bool:
    stat, _, _ = proc.run([
        '/usr/bin/security', 'find-generic-password',
        '-s', _SERVICE, '-a', _account()])
    return stat == 0


def get_password() -> Optional[str]:
    stat, out, _ = proc.run([
        '/usr/bin/security', 'find-generic-password',
        '-s', _SERVICE, '-a', _account(), '-w'])
    if stat != 0:
        return None
    # security -w outputs the password followed by a newline; strip only
    # command-output line endings, never user-intentional spaces/tabs.
    return out.rstrip('\r\n')


def set_password(password: str) -> None:
    # Recreate the item so the "allow all applications" ACL (-A) is always applied,
    # which is required for silent reads from this unsigned app.
    clear_password()
    proc.run([
        '/usr/bin/security', 'add-generic-password',
        '-s', _SERVICE, '-a', _account(), '-w', password, '-A', '-U'])


def clear_password() -> None:
    proc.run([
        '/usr/bin/security', 'delete-generic-password',
        '-s', _SERVICE, '-a', _account()])
