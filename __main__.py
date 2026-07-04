from __future__ import annotations

import fcntl
import json
import logging
import os
import subprocess
import sys
import time

from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
from PyObjCTools import AppHelper

from app.core.logging_setup import install_excepthook, setup_logging
from app.platform.platform import Platform
from app.res.const import Const
from app.ui.app_delegate import AppDelegate


log = logging.getLogger(__name__)


def _activate_existing_instance() -> None:
    """Try to bring an already-running instance to the foreground."""
    try:
        from AppKit import NSRunningApplication
        running = NSRunningApplication.runningApplicationsWithBundleIdentifier_(
            Const.bundle_id)
        if running:
            running[0].activateWithOptions_(1 << 1)  # NSApplicationActivateIgnoringOtherApps
    except Exception:
        pass


def _acquire_instance_lock() -> int | None:
    """Acquire an exclusive file lock to enforce a single running instance.

    Returns the lock file descriptor on success, or None if another instance
    already holds the lock. The descriptor must stay open for the process
    lifetime; closing it releases the lock.
    """
    os.makedirs(Const.config_dir, exist_ok=True)
    lock_path = os.path.join(Const.config_dir, 'instance.lock')
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (OSError, IOError):
        os.close(fd)
        _activate_existing_instance()
        return None
    try:
        os.ftruncate(fd, 0)
        os.write(fd, str(os.getpid()).encode())
    except OSError:
        pass
    return fd


def _diagnose_bluetooth() -> None:
    """Print diagnostic info about Bluetooth device discovery (source or frozen)."""
    from app.platform.bluetooth import _system_profiler_devices, is_powered_on, paired_devices

    log.info('=== Bluetooth Diagnostic ===')
    log.info(f'Python: {sys.executable}')
    log.info(f'Has MEIPASS: {hasattr(sys, "_MEIPASS")}')

    log.info('--- system_profiler ---')
    try:
        sp = _system_profiler_devices()
        log.info(f'count: {len(sp)}')
        for d in sp:
            log.info(f'  {d.name} {d.address} connected={d.connected} rssi={d.rssi}')
    except Exception:
        log.exception('system_profiler failed')

    log.info('--- paired_devices() ---')
    try:
        pd = paired_devices()
        log.info(f'count: {len(pd)}')
        for d in pd:
            log.info(f'  {d.name} {d.address} connected={d.connected} rssi={d.rssi}')
        if pd:
            first = pd[0]
            log.info(f'--- info({first.address}) ---')
            from app.platform.bluetooth import info
            log.info(f'  {info(first.address)}')
    except Exception:
        log.exception('paired_devices failed')

    log.info('--- is_powered_on() ---')
    try:
        log.info(f'{is_powered_on()}')
    except Exception:
        log.exception('is_powered_on failed')

    log.info('--- raw system_profiler JSON ---')
    try:
        proc = subprocess.run(
            ['/usr/sbin/system_profiler', 'SPBluetoothDataType', '-json'],
            capture_output=True, text=True, encoding='utf-8', timeout=8)
        log.info(f'returncode: {proc.returncode}')
        log.info(f'stdout length: {len(proc.stdout)}')
        try:
            data = json.loads(proc.stdout)
            entries = data.get('SPBluetoothDataType') or []
            for entry in entries:
                log.info(f'controller_state: {entry.get("controller_properties", {}).get("controller_state")}')
                log.info(f'connected: {len(entry.get("device_connected") or [])}')
                log.info(f'not_connected: {len(entry.get("device_not_connected") or [])}')
        except Exception:
            log.exception('JSON parse error')
    except Exception:
        log.exception('system_profiler subprocess failed')

    log.info('--- IOBluetooth direct (isolated subprocess) ---')
    try:
        proc = subprocess.run(
            [sys.executable, '-c',
             'from IOBluetooth import IOBluetoothDevice; '
             'd=IOBluetoothDevice.pairedDevices(); '
             'print("paired", len(d or [])); '
             '[print(" ", x.name(), x.addressString(), x.isConnected()) for x in (d or [])]'],
            capture_output=True, text=True, encoding='utf-8', timeout=10)
        log.info(f'returncode: {proc.returncode}')
        if proc.returncode == 0:
            log.info(proc.stdout)
        else:
            log.info(f'stderr: {proc.stderr}')
            log.info('Direct IOBluetooth requires a running NSApplication/NSRunLoop.')
    except Exception:
        log.exception('IOBluetooth direct check failed')


def run() -> None:
    logger = setup_logging(logging.INFO)

    if '--diagnose-bluetooth' in sys.argv:
        _diagnose_bluetooth()
        return

    lock_fd = _acquire_instance_lock()
    if lock_fd is None:
        logger.info('Another instance is already running; exiting.')
        return

    try:
        def on_crash(exc):
            try:
                # Import is deferred to avoid loading AppKit at logging setup time.
                from AppKit import NSApplication
                app = NSApplication.sharedApplication()
                delegate = app.delegate()
                if delegate is not None:
                    delegate.platform.notify(
                        delegate.lang.title_crash, '', str(exc))
            except Exception:
                pass

        install_excepthook(logger, on_crash=on_crash)

        app = NSApplication.sharedApplication()
        platform = Platform()
        delegate = AppDelegate.alloc().initWithPlatform_(platform)
        app.setDelegate_(delegate)
        app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        logger.info(f'Starting {__name__} UnlockerX')
        # The LSUIElement entry is injected by the build step; this is a runtime guard.
        AppHelper.runEventLoop()
    finally:
        os.close(lock_fd)


def main() -> int:
    run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
