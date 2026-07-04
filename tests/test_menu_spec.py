from __future__ import annotations

from app.core.config import Config
from app.core.i18n import load_language
from app.ui.menu_spec import build_spec


def test_build_spec_has_expected_top_level_keys():
    lang = load_language('en')
    spec = build_spec(lang, Config())
    keys = [item.key for item in spec if item.key != '-']
    assert keys == [
        'device_name', 'device_address', 'device_signal', 'device_status',
        'bind_bluetooth_device', 'pause', 'preferences', 'select_language',
        'check_update', 'about', 'quit',
    ]


def test_build_spec_preferences_does_not_contain_select_language():
    lang = load_language('en')
    spec = build_spec(lang, Config())
    prefs = next(item for item in spec if item.key == 'preferences')
    assert not any(c.key == 'select_language' for c in prefs.children)


def test_build_spec_preferences_contains_advanced_options():
    lang = load_language('en')
    spec = build_spec(lang, Config())
    prefs = next(item for item in spec if item.key == 'preferences')
    advanced = next((c for c in prefs.children if c.key == 'advanced_options'), None)
    assert advanced is not None
    assert advanced.kind == 'submenu'
    assert any(c.key == 'export_log' for c in advanced.children)
    assert any(c.key == 'clear_config' for c in advanced.children)
