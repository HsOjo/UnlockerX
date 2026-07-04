from __future__ import annotations

from app.core import decisions
from app.core.ports import IconState


def test_weak_signal_edge_falling_into_weak():
    # crossing down into weak triggers True
    assert decisions.weak_signal_edge(-85, -70, -80) is True


def test_weak_signal_edge_rising_into_strong():
    # crossing up back to strong triggers False
    assert decisions.weak_signal_edge(-70, -85, -80) is False


def test_weak_signal_edge_no_edge_when_staying_weak():
    # both readings weak, no transition
    assert decisions.weak_signal_edge(-90, -85, -80) is None


def test_weak_signal_edge_no_edge_when_staying_strong():
    assert decisions.weak_signal_edge(-60, -70, -80) is None


def test_weak_signal_edge_first_reading_weak():
    # first reading (prev None) that is weak counts as falling edge
    assert decisions.weak_signal_edge(-90, None, -80) is True


def test_weak_signal_edge_none_rssi():
    assert decisions.weak_signal_edge(None, -70, -80) is None


def test_is_weak_signal_none():
    assert decisions.is_weak_signal(None, -80) is False


def test_pick_icon():
    assert decisions.pick_icon(False, False) is IconState.DISCONNECT
    assert decisions.pick_icon(False, True) is IconState.DISCONNECT
    assert decisions.pick_icon(True, True) is IconState.WEAK
    assert decisions.pick_icon(True, False) is IconState.NORMAL


def test_weak_signal_edge_jitter_inside_hysteresis_band_is_not_an_edge():
    # Once weak, small RSSI improvements inside the hysteresis band do not flip back.
    assert decisions.weak_signal_edge(-82, -85, -80) is None
    assert decisions.weak_signal_edge(-79, -82, -80) is None
    # From strong, a small degradation that stays above the weak threshold does not flip.
    assert decisions.weak_signal_edge(-79, -70, -80) is None


def test_weak_signal_edge_rising_must_clear_hysteresis():
    # Rising only triggers when RSSI clears threshold + 3 dB hysteresis.
    assert decisions.weak_signal_edge(-76, -85, -80) is False


def test_should_lock_conditions():
    now = 100.0
    # due, weak, unlocked, not paused -> lock
    assert decisions.should_lock(now, 90.0, True, True, False, False) is True
    # not due yet
    assert decisions.should_lock(now, 110.0, True, True, False, False) is False
    # no scheduled time
    assert decisions.should_lock(now, None, True, True, False, False) is False
    # already locked
    assert decisions.should_lock(now, 90.0, True, True, True, False) is False
    # paused
    assert decisions.should_lock(now, 90.0, True, True, False, True) is False
    # connected and strong -> no reason to lock
    assert decisions.should_lock(now, 90.0, False, True, False, False) is False
    # disconnected -> lock even if strong
    assert decisions.should_lock(now, 90.0, False, False, False, False) is True


def test_should_attempt_unlock_conditions():
    # present, locked, active user -> attempt
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=False, lid=False,
        display_sleep=False, is_wake=False, is_idle=False, paused=False) is True
    # not locked
    assert decisions.should_attempt_unlock(
        is_locked=False, is_connected=True, is_weak=False, lid=False,
        display_sleep=False, is_wake=False, is_idle=False, paused=False) is False
    # disconnected
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=False, is_weak=False, lid=False,
        display_sleep=False, is_wake=False, is_idle=False, paused=False) is False
    # weak
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=True, lid=False,
        display_sleep=False, is_wake=False, is_idle=False, paused=False) is False
    # lid closed
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=False, lid=True,
        display_sleep=False, is_wake=False, is_idle=False, paused=False) is False
    # display sleeping
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=False, lid=False,
        display_sleep=True, is_wake=False, is_idle=False, paused=False) is False
    # idle and not waking -> do not unlock
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=False, lid=False,
        display_sleep=False, is_wake=False, is_idle=True, paused=False) is False
    # idle but waking -> unlock
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=False, lid=False,
        display_sleep=False, is_wake=True, is_idle=True, paused=False) is True
    # paused
    assert decisions.should_attempt_unlock(
        is_locked=True, is_connected=True, is_weak=False, lid=False,
        display_sleep=False, is_wake=False, is_idle=False, paused=True) is False


def test_retry_exhausted():
    assert decisions.retry_exhausted(2, 3) is False
    assert decisions.retry_exhausted(3, 3) is True
    assert decisions.retry_exhausted(4, 3) is True
