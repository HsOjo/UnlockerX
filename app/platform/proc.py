from __future__ import annotations

import subprocess
from typing import Optional, Sequence


def run(args: Sequence[str], input_text: Optional[str] = None,
        timeout: Optional[float] = None) -> tuple[int, str, str]:
    """Run a command with explicit utf-8 decoding. Returns (returncode, stdout, stderr)."""
    with subprocess.Popen(
        list(args), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, encoding='utf-8') as p:
        try:
            out, err = p.communicate(input_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            try:
                out, err = p.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                out, err = '', ''
            return -1, out or '', err or ''
    return p.returncode, out, err


def out(args: Sequence[str], **kwargs) -> str:
    return run(args, **kwargs)[1]
