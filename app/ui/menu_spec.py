from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MenuItem:
    key: str
    title: str = ""
    kind: str = "normal"  # normal | separator | submenu | check
    checked: bool = False
    children: list["MenuItem"] = field(default_factory=list)
    action: str = ""  # menu key used by MenuController; defaults to key

    def __post_init__(self):
        if not self.action:
            self.action = self.key


MenuSpec = list[MenuItem]


def build_spec(lang, config) -> MenuSpec:
    """Create the full menu tree. Titles use the current language."""
    from app.core.config import Config

    _lang = lang
    _cfg: Config = config
    return [
        MenuItem("device_name", _lang.view_device_name(_lang.none)),
        MenuItem("device_address", _lang.view_device_address(_lang.none)),
        MenuItem("device_signal", _lang.view_device_signal(_lang.none)),
        MenuItem("device_status", _lang.view_status(_lang.status_disconnect)),
        MenuItem("-", kind="separator"),
        MenuItem("bind_bluetooth_device", _lang.menu_bind_bluetooth_device),
        MenuItem("-", kind="separator"),
        MenuItem("pause", _lang.menu_pause, kind="check", checked=False),
        MenuItem("-", kind="separator"),
        MenuItem(
            "preferences",
            _lang.menu_preferences,
            kind="submenu",
            children=[
                MenuItem(
                    "set_bluetooth_refresh_rate", _lang.menu_set_bluetooth_refresh_rate
                ),
                MenuItem("set_weak_signal_value", _lang.menu_set_weak_signal_value),
                MenuItem("-", kind="separator"),
                MenuItem(
                    "set_weak_signal_lock_delay", _lang.menu_set_weak_signal_lock_delay
                ),
                MenuItem(
                    "set_disconnect_lock_delay", _lang.menu_set_disconnect_lock_delay
                ),
                MenuItem("set_unlock_delay", _lang.menu_set_unlock_delay),
                MenuItem("-", kind="separator"),
                MenuItem(
                    "signal_value_visible_on_icon",
                    _lang.menu_signal_value_visible_on_icon,
                    kind="check",
                    checked=_cfg.signal_value_visible_on_icon,
                ),
                MenuItem("-", kind="separator"),
                MenuItem("set_password", _lang.menu_set_password),
                MenuItem("clear_password", _lang.menu_clear_password),
                MenuItem("-", kind="separator"),
                MenuItem(
                    "set_startup", _lang.menu_set_startup, kind="check", checked=False
                ),  # updated at runtime
                MenuItem("-", kind="separator"),
                MenuItem(
                    "advanced_options",
                    _lang.menu_advanced_options,
                    kind="submenu",
                    children=[
                        MenuItem("export_log", _lang.menu_export_log),
                        MenuItem("-", kind="separator"),
                        MenuItem("clear_config", _lang.menu_clear_config),
                    ],
                ),
            ],
        ),
        MenuItem("select_language", _lang.menu_select_language),
        MenuItem("-", kind="separator"),
        MenuItem("check_update", _lang.menu_check_update),
        MenuItem("about", _lang.menu_about),
        MenuItem("-", kind="separator"),
        MenuItem("quit", _lang.menu_quit),
    ]
