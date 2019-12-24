from .base.config import ConfigBase


class Config(ConfigBase):
    _protect_fields = [
        'password',
    ]
    welcome = True
    password = ''
    language = 'en'
    device_address = ''
    weak_signal_value = -80
    weak_signal_lock_delay = 6
    disconnect_lock_delay = 10
    use_screen_saver_replace_lock = True
    use_bluetooth_connector_replace_connect = False
    bluetooth_refresh_rate = 1
    signal_value_visible_on_icon = False

    event_signal_weak = ''
    event_connect_status_changed = ''
    event_lock_status_changed = ''
    event_lid_status_changed = ''
