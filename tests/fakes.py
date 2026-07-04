from __future__ import annotations

from typing import Optional

from app.core.ports import DeviceInfo, IconState


class FakeClock:
    def __init__(self, t: float = 1000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


class FakePlatform:
    def __init__(self):
        self.password: Optional[str] = None
        self.unlock_result = True
        self.unlock_calls = 0
        self.lock_calls = 0
        self.connect_calls: list[str] = []

        self.lid = False
        self.idle = 0.0
        self.display_sleep_stat = False
        self.locked = False
        self.device: Optional[DeviceInfo] = None
        self.paired: list[DeviceInfo] = []
        self.require_password_wake_called = False
        self.login_startup = False
        self.notifications: list[tuple[str, str, str]] = []

    # password
    def has_password(self) -> bool:
        return self.password is not None

    def set_password(self, password: str) -> None:
        self.password = password

    def clear_password(self) -> None:
        self.password = None

    def verify_password(self, password: str) -> bool:
        return True

    # unlock / lock
    def unlock(self) -> bool:
        self.unlock_calls += 1
        if self.unlock_result:
            self.locked = False
        return self.unlock_result

    def lock(self) -> None:
        self.lock_calls += 1
        self.locked = True

    # bluetooth
    def bluetooth_info(self, address: str) -> Optional[DeviceInfo]:
        return self.device

    def connect(self, address: str) -> bool:
        self.connect_calls.append(address)
        return True

    def paired_devices(self) -> list[DeviceInfo]:
        return self.paired

    # system
    def check_lid(self) -> Optional[bool]:
        return self.lid

    def idle_time(self) -> float:
        return self.idle

    def display_sleep(self) -> bool:
        return self.display_sleep_stat

    def is_locked(self) -> bool:
        return self.locked

    def set_require_password_wake(self) -> None:
        self.require_password_wake_called = True

    def notify(self, title: str, subtitle: str, body: str) -> None:
        self.notifications.append((title, subtitle, body))

    def accessibility_granted(self) -> bool:
        return True

    def open_accessibility_settings(self) -> None:
        pass

    def open_bluetooth_settings(self) -> None:
        pass

    def bluetooth_powered_on(self) -> bool:
        return True

    # lifecycle
    def has_login_startup(self) -> bool:
        return self.login_startup

    def set_login_startup(self, enable: bool) -> bool:
        self.login_startup = enable
        return True

    def restart(self) -> None:
        pass


class FakeUI:
    def __init__(self):
        self.icon: Optional[IconState] = None
        self.title: Optional[str] = None
        self.status_text = ''
        self.device_text = ('', '', '')
        self.menu_states: dict[str, bool] = {}
        self.notifications: list[tuple[str, str, str]] = []

    def set_icon(self, state: IconState) -> None:
        self.icon = state

    def set_title(self, text: Optional[str]) -> None:
        self.title = text

    def set_status_text(self, text: str) -> None:
        self.status_text = text

    def set_device_text(self, name: str, address: str, signal: str) -> None:
        self.device_text = (name, address, signal)

    def set_menu_state(self, key: str, on: bool) -> None:
        self.menu_states[key] = on

    def notify(self, title: str, subtitle: str, body: str) -> None:
        self.notifications.append((title, subtitle, body))
