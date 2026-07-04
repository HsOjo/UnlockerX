from __future__ import annotations

from app.core.config import Config
from app.core.i18n import load_language
from app.core.ports import DeviceInfo, IconState
from app.core.state_machine import StateMachine
from app.res.const import Const
from tests.fakes import FakeClock, FakePlatform, FakeUI


def make_machine(**config_kwargs):
    config = Config(device_address='AA', bluetooth_refresh_rate=1.0,
                    weak_signal_value=-80, weak_signal_lock_delay=10.0,
                    disconnect_lock_delay=30.0, unlock_delay=2.0)
    for k, v in config_kwargs.items():
        setattr(config, k, v)
    platform = FakePlatform()
    ui = FakeUI()
    clock = FakeClock()
    sm = StateMachine(config, platform, ui, load_language('en'), clock=clock)
    return sm, platform, ui, clock


ENGLISH = load_language('en')


def connected(rssi):
    return DeviceInfo(name='Dev', address='AA', connected=True, rssi=rssi)


def test_weak_signal_schedules_and_cancels_lock():
    sm, platform, ui, clock = make_machine()
    platform.device = connected(-70)
    sm.poll()  # initial: connected, strong
    assert sm.is_connected is True
    assert sm.lock_time is None

    # signal drops into weak -> schedule lock
    clock.advance(2)
    platform.device = connected(-90)
    sm.poll()
    assert sm.is_weak is True
    assert sm.lock_time == clock.t + sm.config.weak_signal_lock_delay

    # signal recovers -> cancel
    clock.advance(2)
    platform.device = connected(-60)
    sm.poll()
    assert sm.is_weak is False
    assert sm.lock_time is None


def test_weak_signal_lock_executes_via_monitor():
    sm, platform, ui, clock = make_machine()
    platform.device = connected(-70)
    sm.poll()
    clock.advance(2)
    platform.device = connected(-90)
    sm.poll()
    lock_time = sm.lock_time

    # before the deadline -> no lock
    sm.monitor(elapsed=0.8)
    assert platform.lock_calls == 0

    # at/after the deadline -> lock
    clock.t = lock_time + 1
    sm.monitor(elapsed=0.8)
    assert platform.lock_calls == 1
    assert platform.locked is True


def test_disconnect_schedules_lock_and_notifies():
    sm, platform, ui, clock = make_machine()
    platform.device = connected(-70)
    sm.poll()
    ui.notifications.clear()

    clock.advance(2)
    platform.device = None
    sm.poll()
    assert sm.is_connected is False
    assert sm.lock_time == clock.t + sm.config.disconnect_lock_delay
    assert any(n[2] == ENGLISH.noti_disconnected for n in ui.notifications)


def test_icon_reflects_state():
    sm, platform, ui, clock = make_machine()
    platform.device = connected(-70)
    sm.poll()
    assert ui.icon is IconState.NORMAL

    clock.advance(2)
    platform.device = connected(-90)
    sm.poll()
    assert ui.icon is IconState.WEAK

    clock.advance(2)
    platform.device = None
    sm.poll()
    assert ui.icon is IconState.DISCONNECT


def test_auto_unlock_when_present_and_locked():
    sm, platform, ui, clock = make_machine()
    platform.set_password('secret')
    platform.idle = 5.0  # above idle_time_short so it is not treated as a manual lock
    platform.locked = True
    platform.device = connected(-70)

    sm.poll()  # detects locked + present, schedules unlock
    assert platform.unlock_calls == 0
    assert sm.unlock_time is not None

    clock.advance(3)  # past unlock_delay and refresh window
    sm.poll()
    assert platform.unlock_calls == 1
    assert any(n[2] == ENGLISH.noti_unlock_success for n in ui.notifications)


def test_manual_lock_is_not_auto_unlocked():
    sm, platform, ui, clock = make_machine()
    platform.set_password('secret')
    platform.idle = 0.0  # user just locked manually
    platform.locked = True
    platform.device = connected(-70)

    sm.poll()
    assert sm.lock_by_user is True
    clock.advance(3)
    sm.poll()
    assert platform.unlock_calls == 0


def test_unlock_retry_limit_auto_pauses():
    sm, platform, ui, clock = make_machine(unlock_delay=0.0)
    platform.set_password('wrong')
    platform.unlock_result = False
    platform.idle = 5.0
    platform.locked = True
    platform.device = connected(-70)

    for _ in range(12):
        clock.advance(2)
        sm.poll()
        if sm.paused:
            break

    assert platform.unlock_calls == Const.unlock_count_limit
    assert sm.paused is True
    assert ui.menu_states.get('pause') is True
    assert any(n[2] == ENGLISH.noti_unlock_error for n in ui.notifications)


def test_lid_close_sets_wake():
    sm, platform, ui, clock = make_machine()
    platform.lid = False
    sm.poll()
    assert sm.is_wake is False
    platform.lid = True
    sm.poll()
    assert sm.is_lid_wake is True
    assert sm.is_wake is True


def test_sleep_gap_sets_wake():
    sm, platform, ui, clock = make_machine()
    sm.monitor(elapsed=0.8)
    assert sm.is_sleep_wake is False
    sm.monitor(elapsed=5.0)
    assert sm.is_sleep_wake is True


def test_pause_toggle():
    sm, platform, ui, clock = make_machine()
    assert sm.toggle_pause() is True
    assert sm.paused is True
    assert ui.menu_states['pause'] is True
    assert sm.toggle_pause() is False
    assert sm.paused is False
