from __future__ import annotations

from unittest.mock import patch

import Quartz

from app.platform import system


def test_display_sleep_true_when_quartz_reports_asleep():
    with patch.object(Quartz, 'CGDisplayIsAsleep', return_value=1):
        with patch.object(Quartz, 'CGMainDisplayID', return_value=42):
            assert system.display_sleep() is True


def test_display_sleep_false_when_quartz_reports_awake():
    with patch.object(Quartz, 'CGDisplayIsAsleep', return_value=0):
        with patch.object(Quartz, 'CGMainDisplayID', return_value=42):
            assert system.display_sleep() is False


def test_display_sleep_falls_back_to_backlight_heuristic():
    with patch.object(Quartz, 'CGDisplayIsAsleep', side_effect=AttributeError):
        ioreg = '"dsyp"={"min"=0,"max"=100,"value"=0}'
        with patch('app.platform.system.proc.out', return_value=ioreg):
            assert system.display_sleep() is True


def test_display_sleep_fallback_unknown_when_no_display():
    with patch.object(Quartz, 'CGDisplayIsAsleep', side_effect=AttributeError):
        with patch('app.platform.system.proc.out', return_value=''):
            assert system.display_sleep() is False
