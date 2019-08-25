from .base.config import ConfigBase


class Config(ConfigBase):
    _protect_fields = [
        'password',
    ]
    welcome = True
    username = ''
    password = ''
    language = 'en'
    event_lock_status_changed = ''
