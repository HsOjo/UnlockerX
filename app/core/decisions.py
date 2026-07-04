from __future__ import annotations

from typing import Optional

from app.core.ports import IconState


_WEAK_HYSTERESIS_DB = 3


def is_weak_signal(rssi: Optional[int], threshold: int) -> bool:
    if rssi is None:
        return False
    return rssi <= threshold


def weak_signal_edge(rssi: Optional[int], rssi_prev: Optional[int], threshold: int) -> Optional[bool]:
    """Return the new weak state only on a real transition, else None.

    A falling edge must cross below ``threshold``; a rising edge must cross
    above ``threshold + _WEAK_HYSTERESIS_DB``. This prevents icon/lock toggling
    when the RSSI jitters around the threshold.
    """
    if rssi is None:
        return None

    weak_threshold = threshold
    strong_threshold = threshold + _WEAK_HYSTERESIS_DB

    is_weak = rssi <= weak_threshold
    was_weak = is_weak_signal(rssi_prev, weak_threshold)
    is_strong = rssi > strong_threshold

    is_decrease = rssi_prev is None or rssi < rssi_prev
    is_increase = rssi_prev is None or rssi > rssi_prev

    if is_decrease and is_weak and not was_weak:
        return True
    if is_increase and was_weak and is_strong:
        return False
    return None


def pick_icon(is_connected: bool, is_weak: bool) -> IconState:
    if not is_connected:
        return IconState.DISCONNECT
    if is_weak:
        return IconState.WEAK
    return IconState.NORMAL


def should_lock(now: float, lock_time: Optional[float], is_weak: bool,
                is_connected: bool, is_locked: bool, paused: bool) -> bool:
    if paused or is_locked or lock_time is None:
        return False
    if now < lock_time:
        return False
    return is_weak or not is_connected


def should_attempt_unlock(is_locked: bool, is_connected: bool, is_weak: bool,
                          lid: Optional[bool], display_sleep: bool,
                          is_wake: bool, is_idle: bool, paused: bool) -> bool:
    if paused or not is_locked or not is_connected or is_weak:
        return False
    if lid or display_sleep:
        return False
    return is_wake or not is_idle


def retry_exhausted(unlock_count: int, limit: int) -> bool:
    return unlock_count >= limit
