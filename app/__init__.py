import threading
import time
from threading import Thread

import rumps

from app import common
from app.lib.blueutil import BlueUtil
from app.util import pyinstaller
from .base.application import ApplicationBase
from .config import Config
from .res.const import Const
from .res.language import load_language, LANGUAGES
from .res.language.english import English
from .util import system_api, osa_api, github, object_convert, log
from .view.application import ApplicationView


class Application(ApplicationBase, ApplicationView):
    def __init__(self):
        ApplicationView.__init__(self)
        ApplicationBase.__init__(self, Config)

        osa_api.set_require_password_wake()

        self.menu_cat = []
        self.init_menu()

        self.blue_util = BlueUtil('%s/app/lib/blueutil/blueutil' % pyinstaller.get_runtime_dir())

        self.is_locked = None  # type: bool
        self.is_connected = None  # type: bool
        self.lock_time = None  # type: float
        self.lid_stat = None  # type: bool
        self.signal_value = None  # type: int

        self.lock_by_user = False
        self.unlock_by_user = False

        self.disable_leave_lock = False
        self.disable_near_unlock = False

        self.hint_set_password = True

        self.cg_session_info = {}
        self.device_info = {}

        self.t_monitor = threading.Thread(target=self.thread_monitor)
        self.t_lock = threading.Lock()

        self.unlock_count = 0

    def bind_menu_callback(self):
        # menu_application
        self.set_menu_callback(self.menu_bind_bluetooth_device, callback=self.bind_bluetooth_device)
        self.set_menu_callback(self.menu_lock_now, callback=lambda _: self.lock_now(True))
        self.set_menu_callback(self.menu_disable_leave_lock,
                               callback=lambda sender: self.set_disable_leave_lock(not sender.state))
        self.set_menu_callback(self.menu_disable_near_unlock,
                               callback=lambda sender: self.set_disable_near_unlock(not sender.state))
        self.set_menu_callback(self.menu_select_language, callback=lambda _: self.select_language())
        self.set_menu_callback(self.menu_check_update, callback=(
            lambda sender: Thread(target=self.check_update, args=(sender,)).start()
        ))
        self.set_menu_callback(self.menu_about, callback=lambda _: self.about())
        self.set_menu_callback(self.menu_quit, callback=lambda _: self.quit())

        # menu_preferences
        self.set_menu_callback(self.menu_set_weak_signal_value,
                               callback=self.generate_callback_config_input(
                                   'weak_signal_value', 'description_set_weak_signal_value', to_int=True))
        self.set_menu_callback(self.menu_set_weak_signal_lock_delay,
                               callback=self.generate_callback_config_input(
                                   'weak_signal_lock_delay', 'description_set_weak_signal_lock_delay', to_int=True))
        self.set_menu_callback(self.menu_set_disconnect_lock_delay,
                               callback=self.generate_callback_config_input(
                                   'disconnect_lock_delay', 'description_set_disconnect_lock_delay', to_int=True))
        self.set_menu_callback(self.menu_set_startup, callback=lambda _: self.set_startup())
        self.set_menu_callback(self.menu_set_password,
                               callback=self.generate_callback_config_input(
                                   'password', 'description_set_password', hidden=True))

        # menu_advanced_options
        self.set_menu_callback(self.menu_export_log, callback=lambda _: self.export_log())
        self.set_menu_callback(self.menu_clear_config, callback=self.clear_config)
        self.set_menu_callback(self.menu_use_screen_saver_replace_lock,
                               callback=self.generate_callback_switch_config('use_screen_saver_replace_lock'))

        # menu_event_callback
        self.set_menu_callback(self.menu_set_signal_weak_event,
                               callback=self.generate_callback_config_input('event_signal_weak',
                                                                            'description_set_event', empty_state=True))
        self.set_menu_callback(self.menu_set_connect_status_changed_event,
                               callback=self.generate_callback_config_input('event_connect_status_changed',
                                                                            'description_set_event', empty_state=True))
        self.set_menu_callback(self.menu_set_lock_status_changed_event,
                               callback=self.generate_callback_config_input('event_lock_status_changed',
                                                                            'description_set_event', empty_state=True))
        self.set_menu_callback(self.menu_set_lid_status_changed_event,
                               callback=self.generate_callback_config_input('event_lid_status_changed',
                                                                            'description_set_event', empty_state=True))

    def set_disable_leave_lock(self, pause):
        self.disable_leave_lock = pause
        self.menu_disable_leave_lock.state = pause

    def set_disable_near_unlock(self, pause):
        self.disable_near_unlock = pause
        self.menu_disable_near_unlock.state = pause

    def bind_bluetooth_device(self, sender):
        devices = {}
        for device in self.blue_util.paired:
            devices[device['name']] = device['address']

        return self.generate_callback_config_select(
            'device_address', self.lang.description_bind_bluetooth_device, devices)(sender)

    def refresh_device_info(self):
        self.set_menu_title(
            'view_device_name', self.lang.view_device_name % (
                self.device_info.get('name', self.lang.none)))

        self.set_menu_title(
            'view_device_address', self.lang.view_device_address % (
                self.device_info.get('address', self.lang.none)))

        self.set_menu_title(
            'view_device_signal_value', self.lang.view_device_signal_value % (
                '%s dBm' % self.signal_value if self.signal_value is not None else self.lang.none))

    def init_menu(self):
        self.setup_menus()
        self.inject_menus()

        self.generate_languages_menu(self.menu_select_language)

        self.bind_menu_callback()
        self.inject_menu_title()
        self.inject_menu_value()

    def inject_menu_value(self):
        self.menu_use_screen_saver_replace_lock.state = self.config.use_screen_saver_replace_lock

    def lock_now(self, by_user=False):
        log.append(self.lock_now, 'Info')
        if not self.is_locked:
            self.lock_time = None
            self.lock_by_user = by_user
            if self.config.use_screen_saver_replace_lock:
                osa_api.screen_save()
            else:
                system_api.sleep(True)

    def lock_delay(self, wait):
        log.append(self.lock_delay, 'Info', wait)
        with self.t_lock:
            if wait is None:
                self.lock_time = None
            else:
                self.lock_time = time.time() + wait

    def unlock(self):
        log.append(self.unlock, 'Info')
        self.refresh_cg_session_info()
        if self.is_locked:
            if self.config.password != '':
                self.unlock_by_user = False
                osa_api.key_stroke(126)
                osa_api.key_stroke('a', modifier='command down')
                osa_api.key_stroke(self.config.password)
                osa_api.key_stroke('return', constant=True)
            elif self.hint_set_password:
                self.hint_set_password = False
                rumps.notification(self.lang.title_info, '', self.lang.noti_password_need)

    def refresh_cg_session_info(self):
        self.cg_session_info = system_api.cgsession_info()
        is_locked_prev = self.is_locked
        is_locked = self.cg_session_info.get('CGSSessionScreenIsLocked', False)
        if is_locked != is_locked_prev:
            self.is_locked = is_locked
            self.callback_lock_status_changed(is_locked, is_locked_prev)

    def callback_refresh(self, sender: rumps.Timer):
        try:
            self.refresh_device_info()
            self.refresh_cg_session_info()

            lid_stat_prev = self.lid_stat
            lid_stat = system_api.check_lid()
            if lid_stat != lid_stat_prev:
                self.lid_stat = lid_stat
                self.callback_lid_status_changed(lid_stat, lid_stat_prev)

            if self.config.device_address is not None:
                device_info_prev = self.device_info
                self.device_info = self.blue_util.info(self.config.device_address)

                is_connected_prev = device_info_prev.get('is_connected')
                is_connected = self.device_info.get('is_connected')
                if is_connected != is_connected_prev:
                    self.is_connected = is_connected
                    self.callback_connect_status_changed(is_connected, is_connected_prev)

                signal_value_prev = device_info_prev.get('signal_value')
                signal_value = self.device_info.get('signal_value')
                if signal_value != signal_value_prev:
                    self.signal_value = signal_value
                    self.callback_signal_value_changed(signal_value, signal_value_prev)

                if self.is_locked and not self.lock_by_user and not self.lid_stat:
                    if signal_value is not None and signal_value > self.config.weak_signal_value:
                        if self.unlock_count < 3:
                            self.unlock()
                        elif self.unlock_count == 3 and self.hint_set_password:
                            rumps.notification(self.lang.title_info, '', self.lang.noti_unlock_error)
                        self.unlock_count += 1
        except:
            sender.stop()
            self.callback_exception()

    def callback_signal_value_changed(self, signal_value: int, signal_value_prev: int = None):
        if signal_value is not None:
            is_weak = signal_value <= self.config.weak_signal_value
            is_weak_prev = True
            if signal_value_prev is not None:
                is_weak_prev = signal_value_prev <= self.config.weak_signal_value

            if (signal_value_prev is not None and signal_value < signal_value_prev) and is_weak and not is_weak_prev:
                self.callback_signal_weak(is_weak, is_weak_prev)
            elif (signal_value_prev is None or signal_value > signal_value_prev) and is_weak_prev and not is_weak:
                self.callback_signal_weak(is_weak, is_weak_prev)

    def callback_signal_weak(self, status: bool, status_prev: bool = None):
        params = locals()

        self.app.icon = '%s/app/res/%s' % (
            pyinstaller.get_runtime_dir(), 'icon_weak_signal.png' if status else 'icon.png')

        if status:
            self.lock_delay(self.config.weak_signal_lock_delay)
        else:
            self.lock_delay(None)

        log.append(self.callback_signal_weak, 'Info', 'from "%s" to "%s"' % (status_prev, status),
                   self.device_info)

        self.event_trigger(self.callback_signal_weak, params, self.config.event_signal_weak)

    def callback_connect_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        self.app.icon = '%s/app/res/%s' % (
            pyinstaller.get_runtime_dir(), 'icon.png' if status else 'icon_disconnect.png')

        if status_prev is not None and not status:
            self.lock_delay(self.config.disconnect_lock_delay)

        log.append(self.callback_connect_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))

        self.event_trigger(self.callback_connect_status_changed, params, self.config.event_connect_status_changed)

    def callback_lid_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        log.append(self.callback_lid_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))

        self.event_trigger(self.callback_lid_status_changed, params, self.config.event_lid_status_changed)

    def callback_lock_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        if status and not status_prev:
            # lock
            self.unlock_by_user = True
        elif status_prev and not status:
            # unlock
            if self.unlock_by_user and not self.lock_by_user and self.config.password != '':
                self.set_disable_leave_lock(True)

            self.lock_by_user = False
            self.hint_set_password = True
            self.unlock_count = 0

        log.append(self.callback_lock_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))

        self.event_trigger(self.callback_lock_status_changed, params, self.config.event_lock_status_changed)

    def thread_monitor(self):
        while True:
            time.sleep(0.5)
            try:
                with self.t_lock:
                    lock_time = self.lock_time

                if not self.disable_leave_lock:
                    if lock_time is not None and time.time() > lock_time:
                        if self.signal_value is None or self.signal_value <= self.config.weak_signal_value:
                            self.lock_now()

                if self.config.device_address is not None:
                    if not self.is_connected:
                        self.blue_util.connect(self.config.device_address)
            except:
                self.callback_exception()
                break

    def welcome(self):
        self.about(True)
        self.select_language()

        self.message_box(self.lang.title_welcome, self.lang.description_welcome_need_accessibility)
        system_api.open_preference('Security', wait=True)
        self.menu_set_password.callback(self.menu_set_password)
        self.message_box(self.lang.title_welcome, self.lang.description_welcome_pair_device)
        system_api.open_preference('Bluetooth', wait=True)
        self.bind_bluetooth_device(self.menu_bind_bluetooth_device)
        self.message_box(self.lang.title_welcome, self.lang.description_welcome_end)

        super().welcome()

    def run(self):
        if self.config.welcome:
            self.welcome()

        t_refresh = rumps.Timer(self.callback_refresh, 1)
        t_refresh.start()

        self.t_monitor.start()
        super().run()
