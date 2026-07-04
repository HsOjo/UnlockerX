from __future__ import annotations

import objc

from app.ui.app_delegate import AppDelegate
from app.ui import app_delegate as app_delegate_module
from tests.fakes import FakePlatform


class _FakeStatusItem:
    def __init__(self, title: str):
        self.title = title
        self.menu = None
        self.icon = None

    def set_menu(self, menu) -> None:
        self.menu = menu

    def set_icon(self, state) -> None:
        self.icon = state

    def set_title(self, text: str | None) -> None:
        pass


def _make_delegate(platform: FakePlatform) -> AppDelegate:
    original = app_delegate_module.StatusItem
    app_delegate_module.StatusItem = _FakeStatusItem
    try:
        return AppDelegate.alloc().initWithPlatform_(platform)
    finally:
        app_delegate_module.StatusItem = original


def test_menu_item_index_uses_string_keys():
    with objc.autorelease_pool():
        platform = FakePlatform()
        delegate = _make_delegate(platform)

    assert all(isinstance(k, str) for k in delegate._menu_items)
    assert 'set_startup' in delegate._menu_items
    assert 'select_language' in delegate._menu_items


def test_refresh_startup_state_updates_checkmark():
    with objc.autorelease_pool():
        platform = FakePlatform()
        delegate = _make_delegate(platform)

    startup_item = delegate._menu_items['set_startup']

    platform.login_startup = False
    delegate._refresh_startup_state()
    assert startup_item.state() == 0

    platform.login_startup = True
    delegate._refresh_startup_state()
    assert startup_item.state() == 1
