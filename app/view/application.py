from rumps import rumps

from app.base.view import ViewBase


class ApplicationView(ViewBase):
    def __init__(self):
        super().__init__()

        self.menu_view_device_name = None  # type: rumps.MenuItem
        self.menu_view_device_address = None  # type: rumps.MenuItem
        self.menu_view_device_signal_value = None  # type: rumps.MenuItem

        self.menu_bind_bluetooth_device = None  # type: rumps.MenuItem
        self.menu_disable_leave_lock = None  # type: rumps.MenuItem
        self.menu_disable_near_unlock = None  # type: rumps.MenuItem
        self.menu_preferences = None  # type: rumps.MenuItem
        self.menu_select_language = None  # type: rumps.MenuItem
        self.menu_check_update = None  # type: rumps.MenuItem
        self.menu_about = None  # type: rumps.MenuItem
        self.menu_quit = None  # type: rumps.MenuItem

        self.menu_set_bluetooth_refresh_rate = None  # type: rumps.MenuItem
        self.menu_set_weak_signal_value = None  # type: rumps.MenuItem
        self.menu_set_weak_signal_lock_delay = None  # type: rumps.MenuItem
        self.menu_set_disconnect_lock_delay = None  # type: rumps.MenuItem
        self.menu_set_startup = None  # type: rumps.MenuItem
        self.menu_set_password = None  # type: rumps.MenuItem
        self.menu_event_callback = None  # type: rumps.MenuItem
        self.menu_advanced_options = None  # type: rumps.MenuItem

        self.menu_signal_value_visible_on_icon = None  # type: rumps.MenuItem
        self.menu_use_screen_saver_replace_lock = None  # type: rumps.MenuItem
        self.menu_use_bluetooth_connector_replace_connect = None  # type: rumps.MenuItem
        self.menu_export_log = None  # type: rumps.MenuItem
        self.menu_clear_config = None  # type: rumps.MenuItem

        self.menu_set_weak_signal_event = None  # type: rumps.MenuItem
        self.menu_set_connect_status_changed_event = None  # type: rumps.MenuItem
        self.menu_set_lock_status_changed_event = None  # type: rumps.MenuItem
        self.menu_set_lid_status_changed_event = None  # type: rumps.MenuItem

    def setup_menus(self):
        # menu_application
        self.add_menu('view_device_name')
        self.add_menu('view_device_address')
        self.add_menu('view_device_signal_value')
        self.add_menu('-')
        self.add_menu('bind_bluetooth_device')
        self.add_menu('-')
        self.add_menu('disable_leave_lock')
        self.add_menu('disable_near_unlock')
        self.add_menu('-')
        self.menu_preferences = self.add_menu('preferences', self.lang.menu_preferences)
        self.add_menu('select_language')
        self.add_menu('-')
        self.add_menu('check_update')
        self.add_menu('about')
        self.add_menu('-')
        self.add_menu('quit')
        # menu_application end

        # menu_preferences
        self.add_menu('set_bluetooth_refresh_rate', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('set_weak_signal_value', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('set_weak_signal_lock_delay', parent=self.menu_preferences)
        self.add_menu('set_disconnect_lock_delay', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('set_startup', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.add_menu('set_password', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.menu_event_callback = self.add_menu('event_callback', parent=self.menu_preferences)
        self.add_menu('-', parent=self.menu_preferences)
        self.menu_advanced_options = self.add_menu('advanced_options', parent=self.menu_preferences)
        # menu_preferences end

        # menu_advanced_options
        self.add_menu('signal_value_visible_on_icon', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('use_screen_saver_replace_lock', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('use_bluetooth_connector_replace_connect', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('export_log', parent=self.menu_advanced_options)
        self.add_menu('-', parent=self.menu_advanced_options)
        self.add_menu('clear_config', parent=self.menu_advanced_options)
        # menu_advanced_options end

        # menu_event_callback
        self.add_menu('set_weak_signal_event', parent=self.menu_event_callback)
        self.add_menu('set_connect_status_changed_event', parent=self.menu_event_callback)
        self.add_menu('-', parent=self.menu_event_callback)
        self.add_menu('set_lock_status_changed_event', parent=self.menu_event_callback)
        self.add_menu('set_lid_status_changed_event', parent=self.menu_event_callback)
        # menu_event_callback end
