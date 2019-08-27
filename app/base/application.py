import os
import sys

import rumps

from app import common
from app.res.const import Const
from app.res.language import LANGUAGES, load_language
from app.res.language.english import English
from app.util import system_api, osa_api, pyinstaller, log, github, object_convert


class ApplicationBase:
    def __init__(self, config_class):
        log.append('app_init', 'Info', 'version: %s' % Const.version, system_api.get_system_version())
        self.app = rumps.App(Const.app_name, quit_button=None)

        self.config = config_class()
        self.config.load()

        self.lang = load_language(self.config.language)  # type: English

        self.menu = {}
        self.menu_check_update = None  # type: rumps.MenuItem

        self.is_admin = system_api.check_admin()

    def add_menu(self, name, title='', callback=None, parent=None):
        if parent is None:
            parent = self.app.menu

        if name == '-':
            parent.add(rumps.separator)
        else:
            if isinstance(name, rumps.MenuItem):
                menu = name
                name = menu.title  # type: str
            else:
                menu = rumps.MenuItem(name)
                parent.add(menu)

            menu.title = title if title != '' else str(name)

            item = {'object': menu, 'name': name, 'callback': None, 'parent': parent}
            self.menu[name] = item
            self.menu[id(menu)] = item
            self.set_menu_callback(name, callback)

            return menu

    def inject_menus(self):
        for k in self.menu:
            if isinstance(k, str):
                key = 'menu_%s' % k
                if hasattr(self, key):
                    setattr(self, key, self.menu[k]['object'])

    def set_menu_title(self, name, title):
        self.app.menu[name].title = title

    def set_menu_callback(self, key, callback=None):
        if not isinstance(key, str):
            key = id(key)

        menu = self.menu[key]
        menu_obj = menu['object']  # type: rumps.MenuItem
        if callback is None:
            menu_obj.set_callback(None)
        else:
            if menu['callback'] is None:
                menu_obj.set_callback(lambda _: self.callback_menu(menu['name']))
            menu['callback'] = callback

    def generate_callback_switch_config(self, key: str):
        """
        Generate switch config field state menu callback function.
        :param key:
        :return: function
        """

        def switch(sender: rumps.MenuItem):
            sender.state = not sender.state
            setattr(self.config, key, bool(sender.state))
            self.config.save()

        return switch

    def generate_callback_config_input(self, key, description, hidden=False, to_int=False, empty_state=False):
        """
        Generate config field input dialog menu callback function.
        """

        def set_input(sender: rumps.MenuItem):
            content = osa_api.dialog_input(sender.title, getattr(self.lang, description),
                                           str(getattr(self.config, key, '')), hidden=hidden)

            if content is not None:
                if to_int:
                    if isinstance(content, str) and content.replace('-', '', 1).isnumeric():
                        setattr(self.config, key, int(content))
                else:
                    setattr(self.config, key, content)

                if empty_state:
                    sender.state = content != ''

                self.config.save()
                return True

            return False

        return set_input

    def generate_callback_config_select(self, key, description, options, multi=False, empty_state=False):
        def select(sender: rumps.MenuItem):
            index = None
            _options = []
            if isinstance(options, dict):
                _options = list(options.keys())
                index = osa_api.choose_from_list(sender.title, description, _options, multi)
            elif isinstance(options, list):
                index = osa_api.choose_from_list(sender.title, description, options, multi)

            if index is not None:
                content = None
                if isinstance(options, dict):
                    content = options[_options[index]]
                elif isinstance(options, list):
                    content = options[index]

                setattr(self.config, key, content)

                if empty_state:
                    sender.state = content != ''

                self.config.save()
                return True

            return False

        return select

    def generate_languages_menu(self, parent):
        g_set_lang = lambda lang: lambda _: self.set_language(lang)
        for i, k in enumerate(LANGUAGES):
            if i > 0:
                self.add_menu('-', parent=parent)
            self.add_menu(k, LANGUAGES[k].l_this, g_set_lang(k), parent=parent)

    def inject_menu_title(self):
        for k, v in self.menu.items():
            if isinstance(k, str) and 'menu_%s' % k in dir(self.lang):
                title = getattr(self.lang, 'menu_%s' % k)
                v['object'].title = title

    def callback_menu(self, name):
        try:
            log.append(self.callback_menu, 'Info', 'Click %s.' % name)
            menu = self.menu[name]
            menu['callback'](menu['object'])
        except:
            self.callback_exception()

    def callback_exception(self):
        exc = common.get_exception()
        log.append(self.callback_exception, 'Error', exc)
        if 'KeyboardInterrupt' in exc:
            self.quit()
        if osa_api.alert(self.lang.title_crash, self.lang.description_crash):
            self.export_log()

    def message_box(self, title, description):
        return osa_api.dialog_select(title, description, [self.lang.ok])

    def run(self):
        self.app.icon = '%s/app/res/icon.png' % pyinstaller.get_runtime_dir()
        self.app.run()

    def quit(self):
        rumps.quit_application()

    def restart(self):
        [_, path] = pyinstaller.get_application_info()
        if path is not None:
            self.quit()
            system_api.open_url(path, True)
        else:
            # quick restart for debug.
            self.app.title = '\x00'
            self.app.icon = None

            path = common.python_path()
            if path is not None:
                os.system('%s %s' % (path, ' '.join(sys.argv)))

        rumps.quit_application()

    def export_log(self):
        folder = osa_api.choose_folder(self.lang.menu_export_log)
        if folder is not None:
            log_str = log.extract_log()
            err_str = log.extract_err()

            for f in self.config._protect_fields:
                v = getattr(self.config, f, '')
                if v != '':
                    log_str = log_str.replace(v, Const.protector)
                    err_str = err_str.replace(v, Const.protector)

            if log_str != '':
                with open('%s/%s' % (folder, '%s.log' % Const.app_name), 'w') as io:
                    io.write(log_str)

            if err_str != '':
                with open('%s/%s' % (folder, '%s.err' % Const.app_name), 'w') as io:
                    io.write(err_str)

    def set_language(self, language):
        self.lang = LANGUAGES[language]()
        self.inject_menu_title()
        self.config.language = language
        self.config.save()

    def select_language(self):
        items = []
        for k in LANGUAGES:
            items.append(LANGUAGES[k].l_this)

        index = osa_api.choose_from_list(English.menu_select_language, English.description_select_language, items)
        if index is not None:
            language = None
            description = items[index]
            for k, v in LANGUAGES.items():
                if description == v.l_this:
                    language = k
                    break

            if language is not None:
                self.set_language(language)
                return True

        return False

    def check_update(self, sender, test=False):
        try:
            release = github.get_latest_release(Const.author, Const.app_name, timeout=5)
            log.append(self.check_update, 'Info', release)

            if test or common.compare_version(Const.version, release['tag_name']):
                rumps.notification(
                    self.lang.noti_update_version % release['name'],
                    self.lang.noti_update_time % release['published_at'],
                    release['body'],
                )

                if sender == self.menu_check_update:
                    if len(release['assets']) > 0:
                        system_api.open_url(release['assets'][0]['browser_download_url'])
                    else:
                        system_api.open_url(release['html_url'])
            else:
                if sender == self.menu_check_update:
                    rumps.notification(sender.title, self.lang.noti_update_none, self.lang.noti_update_star)
        except:
            log.append(self.check_update, 'Warning', common.get_exception())
            if sender == self.menu_check_update:
                rumps.notification(sender.title, '', self.lang.noti_network_error)

    def about(self, welcome=False):
        res = osa_api.dialog_input(self.lang.menu_about if not welcome else self.lang.title_welcome,
                                   self.lang.description_about, Const.github_page)

        if isinstance(res, str):
            res = res.strip().lower()

        if res == ':export log':
            self.export_log()
        elif res == ':check update':
            self.check_update(self.menu_check_update, True)
        elif res == ':restart':
            self.restart()
        elif res == ':debug':
            rumps.debug_mode(True)
        elif res == Const.github_page.lower() and not welcome:
            system_api.open_url(Const.github_page)
        else:
            return res

    def welcome(self):
        self.config.welcome = False
        self.config.save()

    def set_startup(self):
        res = osa_api.alert(self.lang.menu_set_startup, self.lang.description_set_startup)
        if res:
            osa_api.set_login_startup(*pyinstaller.get_application_info())

    def clear_config(self, sender: rumps.MenuItem):
        if osa_api.alert(sender.title, self.lang.description_clear_config):
            self.config.clear()
            if osa_api.alert(sender.title, self.lang.description_clear_config_restart):
                self.restart()

    def event_trigger(self, source, params: dict, path_event: str):
        if path_event != '':
            params_pop = []
            for k, v in params.items():
                if type(v) not in [None.__class__, bool, int, float, str, list, dict]:
                    params_pop.append(k)
            for k in params_pop:
                params.pop(k)

            [stat, out, err] = common.execute(
                path_event, env={Const.app_env: object_convert.to_json(params)}, sys_env=False,
                timeout=self.config.process_timeout)
            log.append(source, 'Event',
                       {'path': path_event, 'status': stat, 'output': out, 'error': err})
