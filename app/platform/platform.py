from __future__ import annotations

from app.core.ports import DeviceInfo, PlatformPort
from app.platform import auth, bluetooth, keychain, lifecycle, lock, notify, system, unlock


class Platform(PlatformPort):
    """Adapter that wires the platform layer to the core protocols."""

    # password / keychain
    def has_password(self) -> bool:
        return keychain.has_password()

    def set_password(self, password: str) -> None:
        keychain.set_password(password)

    def clear_password(self) -> None:
        keychain.clear_password()

    def verify_password(self, password: str) -> bool:
        return auth.verify_password(password)

    # unlock / lock
    def unlock(self) -> bool:
        return unlock.unlock()

    def lock(self) -> None:
        lock.screen_save()

    # bluetooth
    def bluetooth_info(self, address: str) -> Optional[DeviceInfo]:
        return bluetooth.info(address)

    def connect(self, address: str) -> bool:
        return bluetooth.connect(address)

    def paired_devices(self) -> list[DeviceInfo]:
        return bluetooth.paired_devices()

    def bluetooth_powered_on(self) -> bool:
        return bluetooth.is_powered_on()

    # system state
    def check_lid(self) -> Optional[bool]:
        return system.check_lid()

    def idle_time(self) -> float:
        return system.idle_time()

    def display_sleep(self) -> bool:
        return system.display_sleep()

    def is_locked(self) -> bool:
        return system.is_locked()

    def set_require_password_wake(self) -> None:
        return lock.set_require_password_wake()

    # notifications
    @staticmethod
    def notify(title: str, subtitle: str, body: str) -> None:
        notify.notify(title, subtitle, body)

    # lifecycle
    @staticmethod
    def accessibility_granted() -> bool:
        return lifecycle.accessibility_granted()

    @staticmethod
    def open_accessibility_settings() -> None:
        return system.open_accessibility_settings()

    @staticmethod
    def open_bluetooth_settings() -> None:
        return system.open_bluetooth_settings()

    @staticmethod
    def has_login_startup() -> bool:
        return lifecycle.has_login_startup()

    @staticmethod
    def set_login_startup(enable: bool) -> bool:
        return lifecycle.set_login_startup(enable)

    @staticmethod
    def restart() -> None:
        return lifecycle.restart()
