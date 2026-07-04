# UnlockerX

Near unlock your Mac by Bluetooth device.

* Unlock your Mac automatically when a paired Bluetooth device is near.
* Lock the screen when the device leaves, the signal becomes weak, the lid closes, the system is idle, or the display sleeps.
* Native menu-bar UI built with PyObjC/AppKit (no rumps, no bundled binaries).
* Native Bluetooth via `IOBluetooth` (no `blueutil` / `BluetoothConnector` binaries).
* Password stored in the macOS Keychain instead of a local obfuscated config file.
* Check for updates manually or on startup.

Event-driven state machine, native PyObjC/AppKit implementation, no bundled binaries.

> Requires **macOS 10.15+**. Source runs require **Python 3.12+**.

* Multi-language support: English, Simplified Chinese, Traditional Chinese, Japanese, Korean.

## Important Security Note

This app must know your macOS login password in order to type it into the lock screen. The password is stored in your macOS Keychain. Because the app is **unsigned**, the Keychain item is created with an ACL that allows any local process running as you to read it silently. This is the trade-off for automatic unlock without elevated privileges or modifying the system authorization chain.

If you are not comfortable with this, do not use the auto-unlock feature. Without Accessibility permission the app will still lock on leave, but it will not unlock automatically.

## Permissions

* **Accessibility** — required for simulating keystrokes to unlock. If denied, the app runs in "lock only" mode.
* **Bluetooth** — required to read connection state and RSSI of the bound device.

## Downloads

See the [Releases Page](../../releases).

## First Open (Unsigned App)

UnlockerX is distributed unsigned. On first launch, Gatekeeper will refuse to open it. Right-click the app and select **Open**, or clear the quarantine attribute:

```bash
xattr -dr com.apple.quarantine /Applications/UnlockerX.app
```

## How To Build

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra build
uv run python build.py          # build dist/UnlockerX.app and dist/UnlockerX-<version>.zip
```

## Report Bug

Export logs (Preferences → Advanced Options) and attach them to a GitHub issue. Exported logs redact private data.
