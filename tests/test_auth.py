from __future__ import annotations

from unittest.mock import patch

from app.platform import auth


@patch('app.platform.auth.getpass.getuser', return_value='testuser')
def test_verify_password_accepts_correct_password(_mock_user):
    with patch('app.platform.auth.proc.run', return_value=(0, '', '')) as m:
        assert auth.verify_password('secret') is True
        args = m.call_args[0][0]
        assert args[:4] == ['/usr/bin/dscl', '.', '-authonly', 'testuser']


@patch('app.platform.auth.getpass.getuser', return_value='testuser')
def test_verify_password_rejects_wrong_password(_mock_user):
    with patch('app.platform.auth.proc.run', return_value=(1, '', 'Invalid credentials')):
        assert auth.verify_password('wrong') is False
