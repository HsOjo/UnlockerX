from __future__ import annotations

from typing import Callable

from AppKit import (
    NSAlert, NSAlertFirstButtonReturn,
    NSMakeRect, NSPopUpButton, NSSecureTextField, NSTextField, NSView,
)

from app.core.config import Config
from app.core.i18n import Language


def _alert_style(title: str, text: str, buttons=None) -> int:
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    if text:
        alert.setInformativeText_(text)
    if buttons is None:
        buttons = ['OK']
    for b in buttons:
        alert.addButtonWithTitle_(b)
    return alert.runModal()


def show_alert(title: str, text: str) -> None:
    _alert_style(title, text)


def confirm(title: str, text: str, ok_text: str = 'OK', cancel_text: str = 'Cancel') -> bool:
    code = _alert_style(title, text, [ok_text, cancel_text])
    return code == NSAlertFirstButtonReturn


def input_text(title: str, description: str, default: str = '',
               secure: bool = False, placeholder: str = '') -> str | None:
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(description)
    alert.addButtonWithTitle_('OK')
    alert.addButtonWithTitle_('Cancel')

    view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 24))
    if secure:
        field = NSSecureTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 24))
    else:
        field = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 24))
    field.setStringValue_(default)
    if placeholder:
        field.setPlaceholderString_(placeholder)
    view.addSubview_(field)
    alert.setAccessoryView_(view)

    code = alert.runModal()
    if code == NSAlertFirstButtonReturn:
        return field.stringValue()
    return None


def select_from_list(title: str, description: str, items: list[str]) -> int | None:
    if not items:
        return None
    alert = NSAlert.alloc().init()
    alert.setMessageText_(title)
    alert.setInformativeText_(description)
    alert.addButtonWithTitle_('OK')
    alert.addButtonWithTitle_('Cancel')

    view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 28))
    popup = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(0, 2, 300, 26))
    for item in items:
        popup.addItemWithTitle_(item)
    view.addSubview_(popup)
    alert.setAccessoryView_(view)

    code = alert.runModal()
    if code == NSAlertFirstButtonReturn:
        return popup.indexOfSelectedItem()
    return None


class Dialogs:
    def __init__(self, lang: Language, config: Config):
        self.lang = lang
        self.config = config

    def about(self) -> None:
        message = self.lang.description_about + '\n\n' + self.lang.description_about_confirm
        if confirm(self.lang.menu_about, message, self.lang.ok, self.lang.cancel):
            from app.platform import system
            from app.res.const import Const
            system.open_url(Const.github_page)

    def set_password(self, platform) -> None:
        pw = input_text(self.lang.menu_set_password,
                        self.lang.description_password_warning,
                        secure=True, placeholder=self.lang.prompt_input_password)
        if pw is None or pw == '':
            return
        if not platform.verify_password(pw):
            show_alert(self.lang.title_info, self.lang.description_password_incorrect)
            return
        platform.set_password(pw)

    def clear_password(self, platform) -> None:
        if confirm(self.lang.menu_clear_password,
                   self.lang.description_clear_password_confirm,
                   self.lang.ok, self.lang.cancel):
            platform.clear_password()

    def bind_bluetooth_device(self, platform, on_select: Callable[[str, str], None]) -> None:
        devices = platform.paired_devices()
        if not devices and not platform.bluetooth_powered_on():
            show_alert(self.lang.title_info, self.lang.description_bluetooth_off)
            platform.open_bluetooth_settings()
            return

        if not devices:
            show_alert(self.lang.title_info, self.lang.description_no_paired_device)
            platform.open_bluetooth_settings()
            return
        names = [d.name or d.address for d in devices]
        index = select_from_list(self.lang.menu_bind_bluetooth_device,
                                 self.lang.description_bind_bluetooth_device, names)
        if index is None:
            return
        device = devices[index]
        on_select(device.address, device.name)

    def select_language(self, on_select: Callable[[str], None]) -> None:
        from app.core.i18n import LANGUAGES, load_language
        load_language()  # ensure LANGUAGES is populated
        items = [lang.l_this for lang in LANGUAGES.values()]
        index = select_from_list(self.lang.menu_select_language,
                                 self.lang.description_select_language, items)
        if index is None:
            return
        code = list(LANGUAGES.keys())[index]
        on_select(code)

    def input_number(self, title: str, description: str, default: float) -> float | None:
        text = input_text(title, description, default=str(default))
        if text is None:
            return None
        try:
            return float(text)
        except ValueError:
            return None
