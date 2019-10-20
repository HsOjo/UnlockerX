from .py2app import Py2App
from .pyinstaller import PyInstaller
from .shell import Shell

app_shell: Shell


def init_app_shell():
    global app_shell
    if PyInstaller.check():
        app_shell = PyInstaller()
    elif Py2App.check():
        app_shell = Py2App()
    else:
        app_shell = Shell()

    return app_shell


def get_app_shell():
    return app_shell
