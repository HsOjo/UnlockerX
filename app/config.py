from .base.config import ConfigBase


class Config(ConfigBase):
    _protect_fields = [
        'password',
    ]
    welcome = True
    username = ''
    password = ''
    language = 'en'
    device_address = ''
    weak_signal_value = -60
    weak_signal_lock_time = 3
    disconnect_lock_time = 10

    event_signal_weak = ''
    event_connect_status_changed = ''
    event_lock_status_changed = ''
    event_lid_status_changed = ''
