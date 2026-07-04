from __future__ import annotations

import logging
import subprocess

from app.res.const import Const


log = logging.getLogger(__name__)


def _escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')


def notify(title: str, subtitle: str, body: str) -> None:
    """Show a notification via osascript.

    The notification title is always the app name; the caller's `title`
    argument is shown as the subtitle. If a `subtitle` is provided, it is
    prepended to the body. Works without code signing, but notifications are
    attributed to the osascript/Script Editor process and clicking them opens
    that app.

    This function is non-blocking: it launches osascript and returns
    immediately.
    """
    display_body = body
    if subtitle:
        display_body = f'{subtitle}\n{body}' if body else subtitle

    script = (
        f'display notification "{_escape(display_body)}" '
        f'with title "{_escape(Const.app_name)}" '
        f'subtitle "{_escape(title)}"'
    )
    try:
        subprocess.Popen(
            ['/usr/bin/osascript', '-e', script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        log.exception('Failed to show osascript notification')
