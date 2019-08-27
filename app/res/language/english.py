from app.res.const import Const
from . import Language


class English(Language):
    l_this = 'English'
    unknown = 'Unknown Str: (%s)'
    cancel = 'Cancel'
    ok = 'OK'
    none = 'None'

    description_about = '''%s Version %s

Near unlock your Mac by Bluetooth device!

Develop by %s.
Below is the link with the project GitHub page.''' % (Const.app_name, Const.version, Const.author)
    description_set_password = '''Set the current user password.
It will use for unlock your Mac.'''
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
    description_bind_bluetooth_device = '''Bind Bluetooth device. If your device not in this list, You should pair your device on "System Preferences" - "Bluetooth" first.'''
    description_set_weak_signal_value = '''Weak signal will trigger weak signal events.
Unit: dBm, The signal value smaller, the signal weaker.'''
    description_set_weak_signal_lock_delay = '''On device weak signal, lock screen delay time.'''
    description_set_disconnect_lock_delay = '''On device disconnect, lock screen delay time.'''
    description_welcome_need_accessibility = '''%s need permissions to unlock your mac.
You need click "Privacy" - "Accessibility" on the next window, And add "%s" to the control list.''' % (
        Const.app_name, Const.app_name)
    description_welcome_pair_device = '''Before bind bluetooth device, You need to pair your bluetooth device on next window.'''
    description_welcome_end = '''Excellent! Now %s will be working.
Enjoy yourself!''' % Const.app_name

    view_device_name = 'Device Name: %s'
    view_device_address = 'Device Address: %s'
    view_device_signal_value = 'Device Signal: %s'

    menu_bind_bluetooth_device = 'Bind Bluetooth Device'
    menu_lock_now = 'Lock Now (Manual Unlock Need)'
    menu_disable_leave_lock = 'Disable Leave Lock'
    menu_disable_near_unlock = 'Disable Near Unlock'
    menu_preferences = 'Preferences'
    menu_advanced_options = 'Advanced Options'
    menu_event_callback = 'Event Callback'
    menu_set_lock_status_changed_event = 'Set Lock Status Changed Event'
    menu_set_lid_status_changed_event = 'Set Lid Status Changed Event'
    menu_set_signal_weak_event = 'Set Signal Weak Event'
    menu_set_connect_status_changed_event = 'Set Connect Status Changed Event'
    menu_set_weak_signal_lock_delay = 'Set Weak Signal Lock Delay'
    menu_set_disconnect_lock_delay = 'Set Disconnect Lock Delay'
    menu_set_weak_signal_value = 'Set Weak Signal Value'
    menu_set_password = 'Set Current User Password'
    menu_select_language = 'Set Language'
    menu_set_startup = 'Set Login Startup'
    menu_check_update = 'Check Update'
    menu_clear_config = 'Clear Config'
    menu_use_screen_saver_replace_lock = 'Use ScreenSaver Replace Lock'
    menu_export_log = 'Export Log File'
    menu_about = 'About'
    menu_quit = 'Quit'

    title_crash = 'Application Crash'
    title_welcome = 'Welcome'
    title_info = 'Infomation'

    noti_update_version = 'Found update: %s'
    noti_update_time = 'Release Time: %s'
    noti_update_none = 'Current is the newest version.'
    noti_update_star = '(If you love this app, give me a star on GitHub, thanks.)'
    noti_network_error = 'The network maybe have some problem, please retry later.'

    noti_password_need = 'Unlock failed! Need set password.'
    noti_unlock_error = 'Unlock failed! Operation invalid.'
