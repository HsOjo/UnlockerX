"""Logging setup: RotatingFileHandler under the config dir + crash excepthook."""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys

from app.res.const import Const


def setup_logging(level=logging.INFO) -> logging.Logger:
    """Configure root logger to write to the app log file and stderr.

    A stale file at the config directory path blocks makedirs for the log dir,
    so any legacy flat config file is removed first (config is migrated before
    this is called).
    """
    if os.path.isfile(Const.config_dir):
        os.unlink(Const.config_dir)
    os.makedirs(Const.log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(level)

    if not logger.handlers:
        file_handler = logging.FileHandler(
            Const.log_path, mode='a', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        logger.addHandler(stream_handler)

    return logger


def install_excepthook(logger: logging.Logger, on_crash=None) -> None:
    """Log uncaught exceptions and optionally notify, then exit non-zero.

    A non-zero exit lets any launch-agent KeepAlive relaunch the app.
    """
    def hook(exc_type, exc_value, tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, tb)
            return
        logger.critical('Uncaught exception', exc_info=(exc_type, exc_value, tb))
        if on_crash is not None:
            try:
                on_crash(exc_value)
            except Exception:
                logger.exception('on_crash handler failed')
        os._exit(1)

    sys.excepthook = hook
