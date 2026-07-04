from __future__ import annotations

import threading
import traceback
from typing import Optional

import logging
import objc
from AppKit import (
    NSApplication, NSApplicationActivationPolicyAccessory,
    NSMenu, NSURL, NSWorkspace,
)
from Foundation import NSObject

from app.core.config import Config
from app.core.i18n import get_language, map_locale
from app.core.ports import IconState, PlatformPort, UIPort
from app.core.state_machine import StateMachine
from app.core.updater import check_update
from app.ui.dialogs import Dialogs, confirm, show_alert
from app.ui.menu_builder import MenuController, build_menu
from app.ui.menu_spec import build_spec
from app.ui.status_item import StatusItem
from app.ui.timer import RepeatingTimer, run_on_main
from app.res.const import Const


def _detect_language() -> str:
    try:
        from Foundation import NSLocale
        ident = NSLocale.preferredLanguages()[0]
        return map_locale(str(ident))
    except Exception:
        return 'en'


class AppDelegate(NSObject):
    """NSApplicationDelegate that owns the state machine and drives UI updates."""

    def initWithPlatform_(self, platform: PlatformPort):
        self = objc.super(AppDelegate, self).init()
        self.platform = platform
        self.config = Config()
        self.config.load(detect_language=_detect_language)
        self.lang = get_language(self.config.language)
        self.state = StateMachine(
            self.config, platform, UIAdapter(self), self.lang,
            accessibility_granted=self.platform.accessibility_granted())
        self.dialogs = Dialogs(self.lang, self.config)
        self.status = StatusItem(Const.app_name)
        self.controller = MenuController.alloc().initWithDispatcher_(self.on_menu)
        self._menu = None
        self._menu_items = {}
        self._paused_title_cached = self.lang.menu_pause
        self._resume_title_cached = self.lang.menu_resume
        self._rebuild_menu()
        self._refresh_startup_state()
        self.status.set_menu(self._menu)
        self.status.set_icon(IconState.DISCONNECT)

        self._poll_timer = RepeatingTimer.alloc().initWithInterval_target_(1.0, self._poll)
        self._view_timer = RepeatingTimer.alloc().initWithInterval_target_(1.0, self._refresh_view)
        self._monitor_timer = RepeatingTimer.alloc().initWithInterval_target_(
            StateMachine.MONITOR_INTERVAL, self._monitor)
        return self

    def applicationDidFinishLaunching_(self, notification) -> None:
        NSApplication.sharedApplication().setActivationPolicy_(
            NSApplicationActivationPolicyAccessory)
        self.platform.set_require_password_wake()
        self._check_first_run()
        self._poll_timer.start()
        self._view_timer.start()
        self._monitor_timer.start()
        threading.Thread(target=self._startup_update_check, daemon=True).start()

    def _check_first_run(self) -> None:
        if self.config.welcome:
            self._welcome()
            return
        # Ask for the password first; the accessibility prompt comes after so the
        # user is not hit with two consecutive alerts before any actionable dialog.
        if not self.platform.has_password():
            show_alert(self.lang.title_info, self.lang.description_need_password)
            self.dialogs.set_password(self.platform)
        if not self.platform.accessibility_granted():
            show_alert(self.lang.title_info, self.lang.description_need_accessibility)
            self.platform.open_accessibility_settings()

    def _welcome(self) -> None:
        self.dialogs.select_language(self._set_language, self.config.language)
        self.dialogs.about()
        self.dialogs.bind_bluetooth_device(
            self.platform,
            lambda addr, name: self._set_device(addr, name))
        self.dialogs.set_password(self.platform)
        if self.platform.accessibility_granted():
            show_alert(self.lang.title_info, self.lang.description_accessibility_enabled)
        else:
            show_alert(self.lang.title_info, self.lang.description_need_accessibility)
            self.platform.open_accessibility_settings()
        show_alert(self.lang.title_welcome, self.lang.description_welcome_end)
        self.config.welcome = False
        self.config.save()

    def _set_device(self, address: str, name: str) -> None:
        self.config.device_address = address
        self.config.device_name = name
        self.config.save()
        self.state.on_device_changed()

    def _rebuild_menu(self) -> None:
        self._menu = build_menu(build_spec(self.lang, self.config), self.controller)
        self._menu_items.clear()
        self._index_items(self._menu)
        self.status.set_menu(self._menu)

    def _index_items(self, menu: NSMenu) -> None:
        for i in range(menu.numberOfItems()):
            item = menu.itemAtIndex_(i)
            if not item:
                continue
            rep = item.representedObject()
            if rep:
                self._menu_items[str(rep)] = item
            sub = item.submenu()
            if sub:
                self._index_items(sub)

    def _refresh_menu_titles(self) -> None:
        if 'device_name' in self._menu_items:
            self._menu_items['device_name'].setTitle_(
                self.lang.view_device_name(self.config.device_name or self.lang.none))
        if 'device_address' in self._menu_items:
            self._menu_items['device_address'].setTitle_(
                self.lang.view_device_address(self.config.device_address or self.lang.none))

    def _set_language(self, code: str) -> None:
        self.lang = get_language(code)
        self.config.language = code
        self.config.save()
        self.dialogs.lang = self.lang
        self.state.lang = self.lang
        self._paused_title_cached = self.lang.menu_pause
        self._resume_title_cached = self.lang.menu_resume
        self._rebuild_menu()
        self._refresh_menu_titles()
        self.state.refresh_view()

    # ---- callbacks from UI ----
    def on_menu(self, key: str) -> None:
        try:
            self._dispatch_menu(key)
        except Exception:
            self._handle_exception()

    def _dispatch_menu(self, key: str) -> None:
        if key == 'quit':
            NSApplication.sharedApplication().terminate_(self)
            return
        if key == 'pause':
            paused = self.state.toggle_pause()
            item = self._menu_items.get('pause')
            if item:
                item.setTitle_(self._resume_title_cached if paused else self._paused_title_cached)
                item.setState_(1 if paused else 0)
            return
        if key == 'bind_bluetooth_device':
            self.dialogs.bind_bluetooth_device(
                self.platform, lambda addr, name: self._set_device(addr, name))
            self._refresh_menu_titles()
            return
        if key == 'set_password':
            self.dialogs.set_password(self.platform)
            return
        if key == 'clear_password':
            self.dialogs.clear_password(self.platform)
            return
        if key == 'set_startup':
            self._toggle_startup()
            return
        if key == 'export_log':
            self._view_log()
            return
        if key == 'clear_config':
            self._clear_config()
            return
        if key == 'select_language':
            self.dialogs.select_language(self._set_language)
            return
        if key == 'check_update':
            threading.Thread(target=self._check_update_manual, daemon=True).start()
            return
        if key == 'about':
            self.dialogs.about()
            return

        # numeric config fields
        config_key = None
        description = None
        if key == 'set_weak_signal_value':
            config_key = 'weak_signal_value'
            description = self.lang.description_set_weak_signal_value
        elif key == 'set_weak_signal_lock_delay':
            config_key = 'weak_signal_lock_delay'
            description = self.lang.description_set_weak_signal_lock_delay
        elif key == 'set_disconnect_lock_delay':
            config_key = 'disconnect_lock_delay'
            description = self.lang.description_set_disconnect_lock_delay
        elif key == 'set_bluetooth_refresh_rate':
            config_key = 'bluetooth_refresh_rate'
            description = self.lang.description_set_bluetooth_refresh_rate
        elif key == 'set_unlock_delay':
            config_key = 'unlock_delay'
            description = self.lang.description_set_unlock_delay

        if config_key:
            current = getattr(self.config, config_key)
            value = self.dialogs.input_number(self._menu_items[key].title(), description, current)
            if value is not None:
                setattr(self.config, config_key, int(value) if config_key == 'weak_signal_value' else value)
                self.config.save()
            return

        if key == 'signal_value_visible_on_icon':
            item = self._menu_items[key]
            new_state = item.state() != 1
            item.setState_(1 if new_state else 0)
            self.config.signal_value_visible_on_icon = new_state
            self.config.save()

    def _refresh_startup_state(self) -> None:
        item = self._menu_items.get('set_startup')
        if item:
            item.setState_(1 if self.platform.has_login_startup() else 0)

    def _toggle_startup(self) -> None:
        want = not self.platform.has_login_startup()
        self.platform.set_login_startup(want)
        self._refresh_startup_state()

    def _view_log(self) -> None:
        url = NSURL.fileURLWithPath_(Const.log_path)
        NSWorkspace.sharedWorkspace().openURL_(url)

    def _clear_config(self) -> None:
        if not confirm(self.lang.menu_clear_config,
                       self.lang.description_clear_config,
                       self.lang.ok, self.lang.cancel):
            return
        self.config.clear()
        show_alert(self.lang.menu_clear_config,
                   self.lang.description_clear_config_restart)

    def _check_update_manual(self) -> None:
        self._do_check_update(by_user=True)

    def _startup_update_check(self) -> None:
        self._do_check_update(by_user=False)

    def _do_check_update(self, by_user: bool) -> None:
        try:
            release, have_new = check_update(timeout=5)
        except Exception:
            if by_user:
                run_on_main(lambda: show_alert(
                    self.lang.menu_check_update, self.lang.noti_network_error))
            return

        if have_new:
            run_on_main(lambda: self._show_update_available(release, by_user))
        elif by_user:
            run_on_main(lambda: show_alert(
                self.lang.menu_check_update,
                self.lang.noti_update_none + '\n' + self.lang.noti_update_star))

    def _show_update_available(self, release, by_user: bool) -> None:
        title = self.lang.noti_update_version(release.name)
        subtitle = self.lang.noti_update_time(release.published_at)
        self.platform.notify(title, subtitle, release.body or '')
        if by_user:
            from app.platform import system
            show_alert(title,
                       f'{subtitle}\n{self.lang.noti_update_star}\n\n{Const.releases_url}')
            if release.download_url:
                system.open_url(release.download_url)

    # ---- timers ----
    def _poll(self) -> None:
        try:
            self.state.poll()
        except Exception:
            self._handle_exception()

    def _monitor(self) -> None:
        # monitor interval is hardcoded in timer allocation; track elapsed simplistically
        self.state.monitor(elapsed=StateMachine.MONITOR_INTERVAL)

    def _refresh_view(self) -> None:
        try:
            self.state.refresh_view()
        except Exception:
            self._handle_exception()

    def _handle_exception(self) -> None:
        exc = traceback.format_exc().strip()
        log.exception('Unhandled exception in UI callback')
        # Show the user only the final error line; the full traceback is in the log.
        last_line = exc.splitlines()[-1] if exc else 'Unknown error'
        show_alert(self.lang.title_crash, last_line)


class UIAdapter(UIPort):
    """Implements the core UIPort by jumping back to the main thread."""

    def __init__(self, delegate: AppDelegate):
        self.delegate = delegate

    def set_icon(self, state: IconState) -> None:
        run_on_main(lambda: self.delegate.status.set_icon(state))

    def set_title(self, text: Optional[str]) -> None:
        run_on_main(lambda: self.delegate.status.set_title(text))

    def set_status_text(self, text: str) -> None:
        def update():
            item = self.delegate._menu_items.get('device_status')
            if item:
                item.setTitle_(text)
        run_on_main(update)

    def set_device_text(self, name: str, address: str, signal: str) -> None:
        def update():
            items = self.delegate._menu_items
            if 'device_name' in items:
                items['device_name'].setTitle_(
                    self.delegate.lang.view_device_name(name or self.delegate.lang.none))
            if 'device_address' in items:
                items['device_address'].setTitle_(
                    self.delegate.lang.view_device_address(address or self.delegate.lang.none))
            if 'device_signal' in items:
                items['device_signal'].setTitle_(
                    self.delegate.lang.view_device_signal(signal or self.delegate.lang.none))
        run_on_main(update)

    def set_menu_state(self, key: str, on: bool) -> None:
        def update():
            item = self.delegate._menu_items.get(key)
            if item:
                item.setState_(1 if on else 0)
                if key == 'pause':
                    item.setTitle_(
                        self.delegate.lang.menu_resume if on else self.delegate.lang.menu_pause)
        run_on_main(update)

    def notify(self, title: str, subtitle: str, body: str) -> None:
        # platform.notify is non-blocking; no need for an extra thread.
        self.delegate.platform.notify(title, subtitle, body)


log = logging.getLogger(__name__)
