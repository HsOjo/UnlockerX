from __future__ import annotations

from unittest.mock import patch

from app.platform import keychain


@patch('app.platform.keychain.getpass.getuser', return_value='testuser')
def test_has_password_invokes_security_find(_mock_user):
    with patch('app.platform.keychain.proc.run', return_value=(0, '', '')) as m:
        assert keychain.has_password() is True
        args = m.call_args[0][0]
        assert args[:2] == ['/usr/bin/security', 'find-generic-password']


@patch('app.platform.keychain.getpass.getuser', return_value='testuser')
def test_get_password_strips_trailing_newlines(_mock_user):
    with patch('app.platform.keychain.proc.run', return_value=(0, 'secret\r\n', '')):
        assert keychain.get_password() == 'secret'


@patch('app.platform.keychain.getpass.getuser', return_value='testuser')
def test_set_password_deletes_then_adds(_mock_user):
    with patch('app.platform.keychain.proc.run', return_value=(0, '', '')) as m:
        keychain.set_password('pw')
        commands = [c.args[0] for c in m.call_args_list]
        assert any(cmd[1] == 'delete-generic-password' for cmd in commands)
        assert any(cmd[1] == 'add-generic-password' for cmd in commands)
        add = [cmd for cmd in commands if cmd[1] == 'add-generic-password'][0]
        assert '-A' in add


@patch('app.platform.keychain.getpass.getuser', return_value='testuser')
def test_clear_password_invokes_security_delete(_mock_user):
    with patch('app.platform.keychain.proc.run', return_value=(0, '', '')) as m:
        keychain.clear_password()
        args = m.call_args[0][0]
        assert args[:2] == ['/usr/bin/security', 'delete-generic-password']
