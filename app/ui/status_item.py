from __future__ import annotations

import os

from AppKit import (
    NSImage, NSStatusBar, NSVariableStatusItemLength,
)
from Foundation import NSMakeRect, NSSize

from app.core.ports import IconState
from app.runtime import get_resource

# Menu bar icons are rendered at 18x18 points (36x36 px on Retina).
_ICON_SIZE = 18.0


class StatusItem:
    def __init__(self, title: str):
        self.status = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength)
        self.status.setMenu_(None)
        self.status.button().setTitle_('')
        self.status.setToolTip_(title)
        self._images = {}
        for state in IconState:
            path = get_resource(self._icon_name(state))
            if os.path.exists(path):
                img = self._resized_icon(path)
                self._images[state] = img

    @staticmethod
    def _icon_name(state: IconState) -> str:
        return {
            IconState.NORMAL: 'icon.png',
            IconState.WEAK: 'icon_weak_signal.png',
            IconState.DISCONNECT: 'icon_disconnect.png',
        }[state]

    @staticmethod
    def _resized_icon(path: str) -> NSImage:
        """Scale the source icon down to the menu bar size and mark as template."""
        source = NSImage.alloc().initWithContentsOfFile_(path)
        source.setScalesWhenResized_(True)

        size = NSSize(_ICON_SIZE, _ICON_SIZE)
        target = NSImage.alloc().initWithSize_(size)
        target.lockFocus()
        source.drawInRect_fromRect_operation_fraction_(
            NSMakeRect(0, 0, _ICON_SIZE, _ICON_SIZE),
            NSMakeRect(0, 0, source.size().width, source.size().height),
            2,  # NSCompositeSourceOver
            1.0)
        target.unlockFocus()
        target.setTemplate_(True)
        return target

    def set_icon(self, state: IconState) -> None:
        img = self._images.get(state)
        if img:
            self.status.setImage_(img)

    def set_title(self, text: str | None) -> None:
        self.status.button().setTitle_(text or '')

    def set_menu(self, menu) -> None:
        self.status.setMenu_(menu)
