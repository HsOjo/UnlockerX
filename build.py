"""Build script: PyInstaller onedir -> unsigned .app -> distribution zip.

Produces `dist/UnlockerX.app` (LSUIElement menubar app) and
`dist/UnlockerX-<version>.zip`. No code signing / notarization.

Usage:
    python build.py            # build .app + zip
    python build.py --no-zip   # build .app only
"""
import os
import plistlib
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from app.res.const import Const


ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
APP_PATH = os.path.join(DIST, f'{Const.app_name}.app')
ICON = os.path.join(ROOT, 'app', 'res', 'icon.icns')


def _clean():
    for d in ('build', 'dist'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    spec = os.path.join(ROOT, f'{Const.app_name}.spec')
    if os.path.exists(spec):
        os.unlink(spec)


def _pyinstaller():
    data_sep = ';' if os.name == 'nt' else ':'
    res_dir = os.path.join('app', 'res')
    data_files = [
        os.path.join(res_dir, 'icon.png'),
        os.path.join(res_dir, 'icon_weak_signal.png'),
        os.path.join(res_dir, 'icon_disconnect.png'),
    ]
    add_data = []
    for f in data_files:
        add_data.extend(['--add-data', f'{f}{data_sep}{res_dir}'])

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm', '--clean',
        '--windowed',
        '--onedir',
        '--target-arch', 'universal2',
        '--name', Const.app_name,
        '--icon', ICON,
        '--osx-bundle-identifier', Const.bundle_id,
        *add_data,
        '__main__.py',
    ]
    print(' '.join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def _patch_info_plist():
    plist_path = os.path.join(APP_PATH, 'Contents', 'Info.plist')
    with open(plist_path, 'rb') as f:
        info = plistlib.load(f)

    info['LSUIElement'] = True
    info['LSMinimumSystemVersion'] = '10.15'
    info['CFBundleName'] = Const.app_name
    info['CFBundleDisplayName'] = Const.app_name
    info['CFBundleShortVersionString'] = Const.version
    info['CFBundleVersion'] = Const.version
    info['NSHumanReadableCopyright'] = f'Copyright (c) {Const.author}. All rights reserved.'
    info.setdefault(
        'NSBluetoothAlwaysUsageDescription',
        f'{Const.app_name} needs Bluetooth access to detect your bound device for auto-unlock.')

    with open(plist_path, 'wb') as f:
        plistlib.dump(info, f)
    print(f'Patched Info.plist: LSUIElement, LSMinimumSystemVersion=10.15, version={Const.version}')


def _zip():
    zip_path = os.path.join(DIST, f'{Const.app_name}-{Const.version}.zip')
    base = os.path.dirname(APP_PATH)
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
        for dirpath, _, files in os.walk(APP_PATH):
            for name in files:
                full = os.path.join(dirpath, name)
                arcname = os.path.relpath(full, base)
                if '__pycache__' in arcname:
                    continue
                zf.write(full, arcname)
    print(f'Wrote {zip_path}')


def _sanity_check():
    exe = os.path.join(APP_PATH, 'Contents', 'MacOS', Const.app_name)
    if not os.path.exists(exe):
        raise RuntimeError(f'PyInstaller did not produce expected executable: {exe}')


def main():
    if sys.platform != 'darwin':
        print('Warning: building on non-macOS; the .app will not be usable.', file=sys.stderr)
    _clean()
    _pyinstaller()
    _sanity_check()
    _patch_info_plist()
    if '--no-zip' not in sys.argv:
        _zip()
    print(f'Done. Unsigned app at {APP_PATH}')
    print(f'First open: right-click -> Open, or `xattr -dr com.apple.quarantine "{APP_PATH}"`.')


if __name__ == '__main__':
    main()
