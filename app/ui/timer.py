from __future__ import annotations

from typing import Callable

import objc
from Foundation import NSObject, NSTimer


class RepeatingTimer(NSObject):
    """NSTimer wrapper. Runs on the main thread, calling a plain Python callable."""

    def initWithInterval_target_(self, interval: float, callback: Callable[[], None]):
        self = objc.super(RepeatingTimer, self).init()
        self.interval = interval
        self.callback = callback
        self.timer = None
        return self

    def start(self) -> None:
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            self.interval, self, 'tick:', None, True)

    def stop(self) -> None:
        if self.timer:
            self.timer.invalidate()
            self.timer = None

    def tick_(self, sender) -> None:
        self.callback()


class CallbackWrapper(NSObject):
    """Wraps a Python callable so it can be invoked on the main thread."""

    def initWithCallback_(self, callback: Callable[[], None]):
        self = objc.super(CallbackWrapper, self).init()
        self.callback = callback
        return self

    def run(self) -> None:
        self.callback()


def run_on_main(callback: Callable[[], None]) -> None:
    wrapper = CallbackWrapper.alloc().initWithCallback_(callback)
    wrapper.performSelectorOnMainThread_withObject_waitUntilDone_('run', None, False)
