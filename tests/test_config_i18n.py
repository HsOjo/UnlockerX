from __future__ import annotations

import os
import tempfile

import pytest

from app.core.config import Config
from app.core.i18n import LANGUAGES, get_language, load_language


def test_config_round_trip():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, 'config.json')
        c = Config()
        c._path = path
        c.device_address = 'AA:BB'
        c.weak_signal_value = -75
        c.save()

        c2 = Config()
        c2._path = path
        c2.load()
        assert c2.device_address == 'AA:BB'
        assert c2.weak_signal_value == -75


def test_config_no_password_field():
    assert not hasattr(Config(), 'password')


def test_config_load_missing_file_is_noop():
    c = Config()
    c._path = '/nonexistent/path/to/config.json'
    c.load()  # must not raise
    assert c.device_address == ''


def _public_names(obj) -> set[str]:
    """Return the set of public attribute names exposed by an instance."""
    return {a for a in dir(obj) if not a.startswith('_')}


def test_all_languages_have_all_fields():
    english = load_language('en')
    english_names = _public_names(english)
    for code in LANGUAGES:
        if code == 'en':
            continue
        lang = load_language(code)
        assert _public_names(lang) == english_names, f'lang {code} names mismatch'


def test_missing_translation_returns_placeholder():
    en = load_language('en')
    assert en.some_missing_key == '? ? ?: (some_missing_key)'


def test_missing_method_raises_attribute_error():
    en = load_language('en')
    with pytest.raises(AttributeError):
        en.view_device_nane


def test_get_language_fallback():
    assert get_language('nope').code == 'en'
    assert get_language('cn').code == 'cn'
