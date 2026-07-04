from __future__ import annotations

import objc
from AppKit import NSMenu, NSMenuItem
from Foundation import NSObject

from app.ui.menu_spec import MenuItem, MenuSpec


class MenuController(NSObject):
    """Single selector target that dispatches via representedObject."""

    def initWithDispatcher_(self, dispatcher):
        self = objc.super(MenuController, self).init()
        self.dispatcher = dispatcher
        return self

    def menuAction_(self, sender) -> None:
        key = sender.representedObject()
        if key and self.dispatcher:
            self.dispatcher(str(key))


def build_menu(spec: MenuSpec, controller: MenuController) -> NSMenu:
    menu = NSMenu.alloc().init()
    for item in spec:
        _add_item(menu, item, controller)
    return menu


def _add_item(menu: NSMenu, item: MenuItem, controller: MenuController) -> None:
    if item.key == '-' or item.kind == 'separator':
        menu.addItem_(NSMenuItem.separatorItem())
        return

    ns = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(item.title, 'menuAction:', '')
    ns.setTarget_(controller)
    ns.setRepresentedObject_(item.action)

    # Display-only items should not be clickable.
    if item.key in ('device_name', 'device_address', 'device_signal', 'device_status'):
        ns.setEnabled_(False)
        ns.setAction_(None)
        ns.setTarget_(None)

    if item.kind == 'check':
        ns.setState_(1 if item.checked else 0)

    if item.kind == 'submenu' and item.children:
        sub = NSMenu.alloc().init()
        for child in item.children:
            _add_item(sub, child, controller)
        ns.setSubmenu_(sub)

    menu.addItem_(ns)
