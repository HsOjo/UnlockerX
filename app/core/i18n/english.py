from app.res.const import Const
from . import Language


class English(Language):
    code = 'en'
    l_this = 'English'

    ok = 'OK'
    cancel = 'Cancel'
    none = 'None'

    unit_dbm = 'dBm'

    status_normal = 'Connected'
    status_weak = 'Weak Signal'
    status_disconnect = 'Disconnected'

    menu_bind_bluetooth_device = 'Bind Bluetooth Device'
    menu_pause = 'Pause'
    menu_resume = 'Resume'
    menu_preferences = 'Preferences'
    menu_set_weak_signal_value = 'Set Weak Signal Value'
    menu_set_weak_signal_lock_delay = 'Set Weak Signal Lock Delay'
    menu_set_disconnect_lock_delay = 'Set Disconnect Lock Delay'
    menu_set_bluetooth_refresh_rate = 'Set Bluetooth Refresh Rate'
    menu_set_unlock_delay = 'Set Unlock Delay'
    menu_signal_value_visible_on_icon = 'Signal Value Visible On Icon'
    menu_set_password = 'Set Current User Password'
    menu_clear_password = 'Clear Stored Password'
    menu_set_startup = 'Set Login Startup'
    menu_advanced_options = 'Advanced Options'
    menu_export_log = 'View Log'
    menu_clear_config = 'Clear Config'
    menu_select_language = 'Set Language'
    menu_check_update = 'Check Update'
    menu_about = 'About'
    menu_quit = 'Quit'

    title_welcome = 'Welcome'
    title_info = 'Information'
    title_crash = 'Application Crash'

    description_set_password = '''Set the current user login password.
It will be used to unlock your Mac.'''
    description_password_warning = '''Note: The password is stored in the macOS Keychain.
Because this app is unsigned, the Keychain item allows access by any local process, so any program running as you could read it. This is the trade-off for password-free automatic unlock without elevated privileges.'''
    description_password_incorrect = '''The password is incorrect. It was not saved.
Please try again.'''
    description_select_language = 'Select your language.'
    description_bind_bluetooth_device = 'Choose a paired Bluetooth device to bind.'
    description_no_paired_device = 'No paired Bluetooth device found. Please pair your device in "System Settings" - "Bluetooth" first.'
    description_bluetooth_off = 'Bluetooth is turned off. Please turn it on in "System Settings" - "Bluetooth".'
    description_set_weak_signal_value = '''Weak signal triggers the leave-lock countdown.
Unit: dBm. The smaller the value, the weaker the signal.'''
    description_set_weak_signal_lock_delay = 'Lock screen delay after the device signal becomes weak.'
    description_set_disconnect_lock_delay = 'Lock screen delay after the device disconnects.'
    description_set_bluetooth_refresh_rate = '''Bluetooth refresh interval.
Unit: second. Minimum is 1 second.'''
    description_set_unlock_delay = 'Delay before unlocking after the device is present.'
    description_need_accessibility = f'''{Const.app_name} needs the "Accessibility" permission to simulate keystrokes and unlock your Mac.
Enable {Const.app_name} under "Privacy & Security" - "Accessibility" in the next window.'''
    description_accessibility_enabled = f'''"Accessibility" is already enabled for {Const.app_name}.'''
    description_cancel_accessibility = f'''You skipped "Accessibility". {Const.app_name} will only lock on leave and will NOT auto-unlock.'''
    description_welcome_pair_device = 'Pair your Bluetooth device in the next window before binding it.'
    description_set_startup = 'Start this app automatically on login?'
    description_clear_config = 'This action will delete the config file. Continue?'
    description_clear_config_restart = 'Config file deleted. Please restart the application.'
    description_clear_password_confirm = 'Remove the stored password from the Keychain?'
    description_need_password = 'No password is stored. Please set your login password to enable automatic unlock.'
    description_about_confirm = 'Open the GitHub project page?'

    prompt_input_password = 'Password:'

    noti_connected = 'Device connected.'
    noti_disconnected = 'Device disconnected.'
    noti_weak_signal_lock = 'Weak signal, locking screen.'
    noti_unlock_success = 'Unlocked automatically.'
    noti_unlock_failed = 'Auto unlock failed.'
    noti_password_need = 'Unlock failed! Please set a password.'
    noti_unlock_error = 'Unlock failed too many times, auto-paused. Please check the password and "Accessibility" settings.'
    noti_update_none = 'Current is the newest version.'
    noti_update_star = '(If you love this app, give me a star on GitHub, thanks.)'
    noti_network_error = 'The network may have some problem, please retry later.'

    def view_device_name(self, name):
        return f'Device Name: {name}'

    def view_device_address(self, address):
        return f'Device Address: {address}'

    def view_device_signal(self, signal):
        return f'Device Signal: {signal}'

    def view_status(self, status):
        return f'Status: {status}'

    description_about = f'''{Const.app_name} Version {Const.version}

Near unlock your Mac by Bluetooth device!

Develop by {Const.author}.'''

    description_welcome_end = f'''Excellent! {Const.app_name} is now working.
Enjoy!'''

    def noti_update_version(self, version):
        return f'Found update: {version}'

    def noti_update_time(self, release_time):
        return f'Release Time: {release_time}'
