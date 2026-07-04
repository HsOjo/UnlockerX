from __future__ import annotations

import time
from typing import Callable, Optional

from app.core import decisions
from app.core.config import Config
from app.core.i18n import Language
from app.core.ports import DeviceInfo, IconState, PlatformPort, UIPort
from app.res.const import Const


class StateMachine:
    """Pure-decision orchestrator. All side effects go through ui.* / platform.*.

    Two entry points are driven by the runtime threads:
      - poll(): gather system/bluetooth state, detect edges, time unlocks (~1s).
      - monitor(elapsed): execute pending locks, keep the connection alive,
        detect wake-from-sleep (~0.8s).
    """

    MONITOR_INTERVAL = 0.8

    def __init__(self, config: Config, platform: PlatformPort, ui: UIPort,
                 lang: Language, clock: Callable[[], float] = time.time,
                 accessibility_granted: bool = True):
        self.config = config
        self.platform = platform
        self.ui = ui
        self.lang = lang
        self.clock = clock
        self.accessibility_granted = accessibility_granted

        self.lid_stat: Optional[bool] = None
        self.idle_time_val: float = 0.0
        self.display_sleep_stat: bool = False
        self.is_locked: bool = False
        self.is_connected: bool = False
        self.signal_value: Optional[int] = None
        self.is_weak: bool = False
        self.device_info: Optional[DeviceInfo] = None

        self.is_sleep_wake: bool = False
        self.is_lid_wake: bool = False
        self.is_idle_wake: bool = False

        self.lock_by_app: bool = False
        self.lock_by_user: bool = False

        self.paused: bool = False
        self.hint_set_password: bool = True

        self.lock_time: Optional[float] = None
        self.unlock_time: Optional[float] = None
        self.unlock_count: int = 0
        self.blue_refresh_time: float = 0.0
        self._icon_state: Optional[IconState] = None

    # ---- derived ----
    @property
    def is_wake(self) -> bool:
        return self.is_lid_wake or self.is_sleep_wake or self.is_idle_wake

    @property
    def is_idle(self) -> bool:
        return self.idle_time_val >= Const.idle_time

    def _reset_wake(self) -> None:
        self.is_sleep_wake = False
        self.is_lid_wake = False
        self.is_idle_wake = False

    # ---- public control ----
    def toggle_pause(self) -> bool:
        self.set_paused(not self.paused)
        return self.paused

    def set_paused(self, paused: bool) -> None:
        self.paused = paused
        self.ui.set_menu_state('pause', paused)
        if not paused:
            self.unlock_count = 0

    def on_device_changed(self) -> None:
        """Called after the bound device changes; reset per-device state."""
        self.device_info = None
        self.signal_value = None
        self.is_weak = False
        self.is_connected = False
        self.lock_time = None
        self.unlock_time = None
        self.blue_refresh_time = 0.0

    # ---- poll cycle ----
    def poll(self) -> None:
        now = self.clock()
        self._refresh_lid()
        self._refresh_idle()
        self.display_sleep_stat = self.platform.display_sleep()
        self._refresh_lock_status()
        self._refresh_bluetooth(now)

    def _refresh_lid(self) -> None:
        prev = self.lid_stat
        cur = self.platform.check_lid()
        if cur != prev:
            self.lid_stat = cur
            if cur and not prev:
                # Lid just closed; when it reopens, treat as a wake event.
                self.is_lid_wake = True

    def _refresh_idle(self) -> None:
        prev = self.idle_time_val
        cur = self.platform.idle_time()
        if cur != prev:
            self.idle_time_val = cur
            if cur < prev and prev >= Const.idle_time:
                # User activity resumed after being idle.
                self.unlock_count = 0
                self.is_idle_wake = self.is_locked

    def _refresh_lock_status(self) -> None:
        prev = self.is_locked
        cur = self.platform.is_locked()
        if cur != prev:
            self.is_locked = cur
            self._on_lock_changed(cur, prev)

    def _on_lock_changed(self, status: bool, status_prev: bool) -> None:
        if status and not status_prev:
            # Locked. Distinguish a manual lock so we don't fight the user.
            if self.idle_time_val < Const.idle_time_short and not self.lock_by_app:
                self.lock_by_user = True
        elif status_prev and not status:
            # Unlocked.
            self._reset_wake()
            self.lock_by_user = False
            self.lock_by_app = False
            self.hint_set_password = True
            self.unlock_count = 0

    def _refresh_bluetooth(self, now: float) -> None:
        address = self.config.device_address
        if not address:
            return
        if now - self.blue_refresh_time < self.config.bluetooth_refresh_rate:
            return
        self.blue_refresh_time = now

        info = self.platform.bluetooth_info(address)
        self.device_info = info
        rssi = info.rssi if info else None
        connected = info.connected if info else False

        if rssi != self.signal_value:
            prev = self.signal_value
            self.signal_value = rssi
            edge = decisions.weak_signal_edge(rssi, prev, self.config.weak_signal_value)
            if edge is not None:
                self.is_weak = edge
                self._on_weak_signal(edge)

        if connected != self.is_connected:
            prev_c = self.is_connected
            self.is_connected = connected
            self._on_connect_changed(connected, prev_c)

        self._refresh_icon()
        self._maybe_unlock(now)

    def _on_weak_signal(self, is_weak: bool) -> None:
        if is_weak:
            self._schedule_lock(self.config.weak_signal_lock_delay)
        else:
            self._schedule_lock(None)

    def _on_connect_changed(self, status: bool, status_prev: bool) -> None:
        if not status:
            self.ui.notify(self.lang.title_info, '', self.lang.noti_disconnected)
            if self.lock_time is None:
                self._schedule_lock(self.config.disconnect_lock_delay)
        else:
            self.ui.notify(self.lang.title_info, '', self.lang.noti_connected)
            if not self.is_weak:
                self._schedule_lock(None)

    def _schedule_lock(self, wait: Optional[float]) -> None:
        if wait is not None and (self.is_locked or self.lid_stat):
            return
        self.lock_time = None if wait is None else self.clock() + wait

    def _maybe_unlock(self, now: float) -> None:
        if not self.accessibility_granted:
            self.unlock_time = None
            return
        if not decisions.should_attempt_unlock(
                self.is_locked, self.is_connected, self.is_weak, self.lid_stat,
                self.display_sleep_stat, self.is_wake, self.is_idle, self.paused):
            self.unlock_time = None
            return

        if self.is_wake and self.unlock_count > Const.unlock_count_limit:
            self.unlock_count = 0

        need_unlock = self.lock_by_app or not self.lock_by_user
        if not (self.is_wake or need_unlock):
            self.unlock_time = None
            return

        if decisions.retry_exhausted(self.unlock_count, Const.unlock_count_limit):
            self.unlock_time = None
            return

        if self.unlock_time is None:
            self.unlock_time = now + self.config.unlock_delay
            return
        if now < self.unlock_time:
            return

        self.unlock_time = None
        self._do_unlock()

    def _do_unlock(self) -> None:
        if not self.platform.has_password():
            if self.hint_set_password:
                self.hint_set_password = False
                self.ui.notify(self.lang.title_info, '', self.lang.noti_password_need)
            return

        ok = self.platform.unlock()
        self.unlock_count += 1

        if ok:
            self.ui.notify(self.lang.title_info, '', self.lang.noti_unlock_success)
        elif decisions.retry_exhausted(self.unlock_count, Const.unlock_count_limit):
            self.set_paused(True)
            self.ui.notify(self.lang.title_info, '', self.lang.noti_unlock_error)
        else:
            self.ui.notify(self.lang.title_info, '', self.lang.noti_unlock_failed)

    # ---- monitor cycle ----
    def monitor(self, elapsed: float) -> None:
        now = self.clock()
        if elapsed > self.MONITOR_INTERVAL * 2:
            self.is_sleep_wake = True

        if decisions.should_lock(now, self.lock_time, self.is_weak,
                                 self.is_connected, self.is_locked, self.paused):
            self._lock_now()

        address = self.config.device_address
        if address and not self.is_connected and not self.lid_stat and (
                not self.display_sleep_stat or self.idle_time_val < Const.idle_time or self.is_wake):
            self.platform.connect(address)

    def _lock_now(self) -> None:
        if self.is_locked or self.is_wake:
            return
        self.lock_time = None
        self.lock_by_app = True
        if self.is_weak and self.is_connected:
            self.ui.notify(self.lang.title_info, '', self.lang.noti_weak_signal_lock)
        self.platform.lock()

    # ---- ui refresh ----
    def _refresh_icon(self) -> None:
        state = decisions.pick_icon(self.is_connected, self.is_weak)
        if state != self._icon_state:
            self._icon_state = state
            self.ui.set_icon(state)

    def refresh_view(self) -> None:
        name = (self.device_info.name if self.device_info else '') or self.lang.none
        address = self.config.device_address or self.lang.none
        if self.signal_value is not None:
            signal = f'{self.signal_value} {self.lang.unit_dbm}'
        else:
            signal = self.lang.none
        self.ui.set_device_text(name, address, signal)

        if not self.is_connected:
            status = self.lang.status_disconnect
        elif self.is_weak:
            status = self.lang.status_weak
        else:
            status = self.lang.status_normal
        self.ui.set_status_text(self.lang.view_status(status))

        self.ui.set_title(signal if self.config.signal_value_visible_on_icon else None)
