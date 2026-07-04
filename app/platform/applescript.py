from __future__ import annotations

from typing import Optional

from app.platform import proc


def run_applescript(code: str, timeout: Optional[float] = None) -> tuple[int, str, str]:
    return proc.run(['/usr/bin/osascript'], input_text=code, timeout=timeout)
