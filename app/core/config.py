from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, fields
from typing import Callable, Optional

from app.res.const import Const


log = logging.getLogger(__name__)


@dataclass
class Config:
    """Persistent settings. Never contains the password (stored in Keychain)."""

    welcome: bool = True
    language: str = ''
    device_address: str = ''
    device_name: str = ''
    weak_signal_value: int = -80
    weak_signal_lock_delay: float = 10.0
    disconnect_lock_delay: float = 30.0
    bluetooth_refresh_rate: float = 1.0
    signal_value_visible_on_icon: bool = False
    unlock_delay: float = 2.0

    _path = Const.config_path

    def load(self, detect_language: Optional[Callable[[], str]] = None) -> None:
        # Migrate legacy flat-file config (~/Library/Application Support/<bundle_id>)
        # to the new directory layout with config.json inside that path.
        if os.path.isfile(Const.config_dir):
            try:
                with open(Const.config_dir, 'r', encoding='utf-8') as io:
                    data = json.load(io)
                os.makedirs(os.path.dirname(self._path), exist_ok=True)
                with open(self._path, 'w', encoding='utf-8') as io:
                    json.dump(data, io, indent='  ', ensure_ascii=False)
                os.unlink(Const.config_dir)
            except (OSError, ValueError):
                pass

        dirty = not os.path.exists(self._path)
        if os.path.exists(self._path):
            try:
                with open(self._path, 'r', encoding='utf-8') as io:
                    data = json.load(io)
            except (OSError, ValueError):
                data = {}
                dirty = True
                log.warning('Failed to load config from %s; using defaults.', self._path)
            else:
                known = {f.name for f in fields(self)}
                for k, v in data.items():
                    if k in known:
                        setattr(self, k, v)
        if not self.language and detect_language:
            self.language = detect_language()
            dirty = True
        # Persist defaults / resolved language only when something changed.
        if dirty:
            self.save()

    def save(self) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, 'w', encoding='utf-8') as io:
            json.dump(asdict(self), io, indent='  ', ensure_ascii=False)

    def clear(self) -> None:
        if os.path.exists(self._path):
            os.unlink(self._path)
