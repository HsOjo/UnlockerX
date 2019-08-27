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

        self.menu_cat = []
        self.init_menu()

        self.blue_util = BlueUtil('%s/app/lib/blueutil/blueutil' % pyinstaller.get_runtime_dir())

        self.is_admin = system_api.check_admin()
        self.is_locked = None  # type: bool
        self.lock_time = None  # type: float
        self.lid_stat = None  # type: bool

        self.lock_by_user = True
        self.unlock_by_user = True

        self.pause_auto_lock = False
        self.pause_auto_unlock = False

        self.cg_session_info = None  # type: dict
        self.device_info = {}  # type: dict

        self.t_monitor = threading.Thread(target=self.thread_monitor)
        self.t_lock = threading.Lock()

    def bind_menu_callback(self):
        # menu_application
        self.set_menu_callback(self.menu_bind_bluetooth_device, callback=self.bind_bluetooth_device)
        self.set_menu_callback(self.menu_lock_now, callback=lambda _: self.lock_now(True))
        self.set_menu_callback(self.menu_pause_auto_lock,
                               callback=lambda sender: self.set_pause_auto_lock(not sender.state))
        self.set_menu_callback(self.menu_pause_auto_unlock,
                               callback=lambda sender: self.set_pause_auto_unlock(not sender.state))
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
        self.set_menu_callback(self.menu_set_weak_signal_lock_time,
                               callback=self.generate_callback_config_input(
                                   'weak_signal_lock_time', 'description_set_weak_signal_lock_time', to_int=True))
        self.set_menu_callback(self.menu_set_disconnect_lock_time,
                               callback=self.generate_callback_config_input(
                                   'disconnect_lock_time', 'description_set_disconnect_lock_time', to_int=True))
        self.set_menu_callback(self.menu_set_startup, callback=lambda _: self.set_startup())
        self.set_menu_callback(self.menu_set_username,
                               callback=self.generate_callback_config_input('username', 'description_set_username'))
        self.set_menu_callback(self.menu_set_password,
                               callback=self.generate_callback_config_input('password', 'description_set_password',
                                                                            hidden=True))

        # menu_advanced_options
        self.set_menu_callback(self.menu_export_log, callback=lambda _: self.export_log())
        self.set_menu_callback(self.menu_clear_config, callback=self.clear_config)

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

    def set_pause_auto_lock(self, pause):
        self.pause_auto_lock = pause
        self.menu_pause_auto_lock.state = pause

    def set_pause_auto_unlock(self, pause):
        self.pause_auto_unlock = pause
        self.menu_pause_auto_unlock.state = pause

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

        signal_value = self.device_info.get('signal_value')
        self.set_menu_title(
            'view_device_signal_value', self.lang.view_device_signal_value % (
                '%s dBm' % signal_value if signal_value is not None else self.lang.none))

    def init_menu(self):
        self.setup_menus()
        self.inject_menus()

        self.generate_languages_menu(self.menu_select_language)

        self.bind_menu_callback()
        self.inject_menu_title()

    def lock_now(self, by_user=False):
        log.append(self.lock_now, 'Info')
        if not self.is_locked:
            self.lock_time = None
            self.lock_by_user = by_user
            # system_api.sleep(True)
            osa_api.screen_save()

    def lock_delay(self, wait):
        with self.t_lock:
            if wait is None:
                self.lock_time = None
            else:
                self.lock_time = time.time() + wait

    def unlock(self):
        if self.config.password != '':
            self.unlock_by_user = False
            osa_api.key_stroke(126)
            osa_api.key_stroke('a', modifier='command down')
            osa_api.key_stroke(self.config.password)
            osa_api.key_stroke('return', constant=True)
        else:
            self.message_box(self.lang.info, self.lang.description_need_set_password)

    def callback_refresh(self, sender: rumps.Timer):
        try:
            self.refresh_device_info()

            self.cg_session_info = system_api.cgsession_info()
            is_locked_prev = self.is_locked
            is_locked = self.cg_session_info.get('CGSSessionScreenIsLocked', False)
            if is_locked != is_locked_prev:
                self.is_locked = is_locked
                self.callback_lock_status_changed(is_locked, is_locked_prev)

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
                    self.callback_connect_status_changed(is_connected, is_connected_prev)

                signal_value_prev = device_info_prev.get('signal_value')
                signal_value = self.device_info.get('signal_value')
                if signal_value != signal_value_prev:
                    self.callback_device_signal_value_changed(signal_value, signal_value_prev)

                print(signal_value, self.is_locked, self.lock_by_user, self.lid_stat)
                if signal_value is not None and signal_value > self.config.weak_signal_value and self.is_locked and not self.lock_by_user and not self.lid_stat:
                    self.unlock()
        except:
            sender.stop()
            self.callback_exception()

    def callback_device_signal_value_changed(self, value: int, value_prev: int = None):
        if value_prev is not None and value is not None:
            is_weak = value <= self.config.weak_signal_value
            is_weak_prev = value_prev <= self.config.weak_signal_value
            if value < value_prev and is_weak and not is_weak_prev:
                self.callback_signal_weak(is_weak, is_weak_prev)
            elif value > value_prev and is_weak_prev and not is_weak:
                self.callback_signal_weak(is_weak, is_weak_prev)

    def callback_signal_weak(self, status: bool, status_prev: bool = None):
        params = locals()

        if status:
            self.lock_delay(self.config.weak_signal_lock_time)
        else:
            self.lock_delay(None)

        log.append(self.callback_signal_weak, 'Info', 'from "%s" to "%s"' % (status_prev, status),
                   self.device_info)

        self.event_trigger(self.callback_signal_weak, params, self.config.event_signal_weak)

    def callback_connect_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        if status_prev is not None and not status:
            self.lock_delay(self.config.disconnect_lock_time)
        elif status and not status_prev:
            if self.device_info['signal_value'] < self.config.weak_signal_value:
                self.callback_signal_weak(True, False)

        log.append(self.callback_connect_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))

        self.event_trigger(self.callback_connect_status_changed, params, self.config.event_connect_status_changed)

    def callback_lid_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        self.lock_by_user = False

        log.append(self.callback_lid_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))

        self.event_trigger(self.callback_lid_status_changed, params, self.config.event_lid_status_changed)

    def callback_lock_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        if status and not status_prev:
            # lock
            if self.lid_stat:
                self.lock_by_user = True
            self.unlock_by_user = True
        elif status_prev and not status:
            # unlock
            if self.unlock_by_user and not self.lock_by_user:
                self.set_pause_auto_lock(True)

        log.append(self.callback_lock_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))

        self.event_trigger(self.callback_lock_status_changed, params, self.config.event_lock_status_changed)

    def thread_monitor(self):
        while True:
            time.sleep(0.5)
            try:
                with self.t_lock:
                    lock_time = self.lock_time

                if lock_time is not None and time.time() > lock_time:
                    signal_value = self.device_info.get('signal_value')
                    if signal_value is None or signal_value <= self.config.weak_signal_value:
                        if not self.pause_auto_lock:
                            self.lock_now()

                if self.config.device_address is not None:
                    if not self.device_info.get('is_connected'):
                        self.blue_util.connect(self.config.device_address)
            except:
                self.callback_exception()
                break

    def welcome(self):
        self.about(True)
        self.select_language()

        super().welcome()

    def run(self):
        if self.config.welcome:
            self.welcome()

        t_refresh = rumps.Timer(self.callback_refresh, 1)
        t_refresh.start()

        self.t_monitor.start()
        super().run()
