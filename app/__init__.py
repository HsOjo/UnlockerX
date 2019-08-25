from threading import Thread

import rumps

from app import common
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

        self.is_admin = system_api.check_admin()
        self.is_locked = None  # type: bool

        self.cgsession_info = None  # type: dict

    def bind_menu_callback(self):
        # menu_application
        self.set_menu_callback(self.menu_lock_now, callback=lambda _: self.lock_now())
        self.set_menu_callback(self.menu_select_language, callback=lambda _: self.select_language())
        self.set_menu_callback(self.menu_check_update, callback=(
            lambda sender: Thread(target=self.check_update, args=(sender,)).start()
        ))
        self.set_menu_callback(self.menu_about, callback=lambda _: self.about())
        self.set_menu_callback(self.menu_quit, callback=lambda _: self.quit())

        # menu_preferences
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
        self.set_menu_callback(self.menu_set_lock_status_changed_event,
                               callback=self.generate_callback_config_input('event_lock_status_changed',
                                                                            'description_set_event', empty_state=True))

    def init_menu(self):
        self.setup_menus()
        self.inject_menus()

        self.generate_languages_menu(self.menu_select_language)

        self.bind_menu_callback()
        self.inject_menu_title()

    def lock_now(self):
        # system_api.sleep(True)
        osa_api.screen_save()

    def unlock(self):
        osa_api.key_stroke('down', constant=True)
        osa_api.key_stroke('a', modifier='command down')
        osa_api.key_stroke(self.config.password)
        osa_api.key_stroke('return', constant=True)

    def callback_refresh(self, sender: rumps.Timer):
        try:
            self.cgsession_info = system_api.cgsession_info()
            is_locked = self.cgsession_info.get('CGSSessionScreenIsLocked', False)
            if is_locked != self.is_locked:
                self.callback_lock_status_changed(is_locked, self.is_locked)
                self.is_locked = is_locked
        except:
            sender.stop()
            self.callback_exception()

    def callback_lock_status_changed(self, status: bool, status_prev: bool = None):
        params = locals()

        log.append(self.callback_lock_status_changed, 'Info', 'from "%s" to "%s"' % (status_prev, status))
        print(self.cgsession_info)

        self.event_trigger(self.callback_lock_status_changed, params, self.config.event_lock_status_changed)

    def welcome(self):
        self.about(True)
        self.select_language()

        super().welcome()

    def run(self):
        if self.config.welcome:
            self.welcome()

        t_refresh = rumps.Timer(self.callback_refresh, 1)
        t_refresh.start()

        super().run()
