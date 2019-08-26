from app.res.const import Const
from . import Language


class English(Language):
    l_this = 'English'
    unknown = 'Unknown Str: (%s)'
    cancel = 'Cancel'
    ok = 'OK'
    none = 'None'

    description_about = '''%s Version %s

Develop by %s.
Below is the link with the project GitHub page.''' % (Const.app_name, Const.version, Const.author)
    description_set_password = '''Set the administrator user password.'''
    description_set_username = '''Set the administrator username. (This username isn't full name! You can query it on "Terminal.app", login your admin user and input "whoami" on terminal.)
(If current user is administrator then this is optional. Will use current username if empty.)'''
    description_select_language = 'Select your language.'
    description_crash = '''Oops! Application Crash!
Will export log later. Send the log file to Developer, please.'''
    description_set_startup = '''Do you want to set startup this app on login?
(You can cancel it on `System Preferences` - `User or Group account` - `Login items`)'''
    description_set_event = '''Input executable program path on here. If this event triggered, will execute this program.
Event parameter will passing through Environment. (JSON Format, key: %s)

More information can found on GitHub "doc/" folder. (such as examples.)''' % Const.app_env
    description_clear_config = '''This action will delete config file, Do it now?'''
    description_clear_config_restart = '''Config file is deleted now, Restart this application now?'''
    description_bind_device = '''Bind Bluetooth device. If your device not in this list, You should pair your device on "System Preferences" - "Bluetooth" first.'''
    description_set_weak_signal_value = '''Weak signal will trigger weak signal events.
Unit: dBm, The signal value smaller, the signal weaker.'''

    view_device_name = 'Device Name: %s'
    view_device_address = 'Device Address: %s'
    view_device_signal_value = 'Device Signal: %s'

    menu_bind_device = 'Bind Device'
    menu_lock_now = 'Lock Now'
    menu_preferences = 'Preferences'
    menu_advanced_options = 'Advanced Options'
    menu_event_callback = 'Event Callback'
    menu_set_lock_status_changed_event = 'Set Lock Status Changed Event'
    menu_set_weak_signal_value = 'Set Weak Signal Value'
    menu_set_username = 'Set Admin Username (Not Admin User Need)'
    menu_set_password = 'Set Admin Password'
    menu_select_language = 'Set Language'
    menu_set_startup = 'Set Login Startup'
    menu_check_update = 'Check Update'
    menu_clear_config = 'Clear Config'
    menu_export_log = 'Export Log File'
    menu_about = 'About'
    menu_quit = 'Quit'

    title_crash = 'Application Crash'
    title_welcome = 'Welcome'

    noti_update_version = 'Found update: %s'
    noti_update_time = 'Release Time: %s'
    noti_update_none = 'Current is the newest version.'
    noti_update_star = '(If you love this app, give me a star on GitHub, thanks.)'
    noti_network_error = 'The network maybe have some problem, please retry later.'
