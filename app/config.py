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
    event_lock_status_changed = ''
    event_device_signal_weak = ''
