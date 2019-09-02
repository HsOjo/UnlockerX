from .base.config import ConfigBase


class Config(ConfigBase):
    _protect_fields = [
        'password',
    ]
    welcome = True
    password = ''
    language = 'en'
    device_address = ''
    weak_signal_value = -60
    weak_signal_lock_delay = 5
    disconnect_lock_delay = 10
    use_screen_saver_replace_lock = True
    bluetooth_refresh_rate = 1

    event_signal_weak = ''
    event_connect_status_changed = ''
    event_lock_status_changed = ''
    event_lid_status_changed = ''
