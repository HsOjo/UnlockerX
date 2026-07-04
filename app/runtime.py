from __future__ import annotations

import os
import sys


def get_runtime_dir() -> str:
    """Return the directory that contains bundled resources."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_resource(name: str) -> str:
    return os.path.join(get_runtime_dir(), 'app', 'res', name)
