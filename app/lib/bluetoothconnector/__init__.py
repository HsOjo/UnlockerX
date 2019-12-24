from app.lib.shell_lib import ShellLib


class BluetoothConnector(ShellLib):
    def connect(self, mac: str, notify: bool = False):
        args = ['-c', mac]
        if notify:
            args.append('-n')
        [stat, _, _] = self.exec(*args)
        return stat == 0

    def disconnect(self, mac: str, notify: bool = False):
        args = ['-d', mac]
        if notify:
            args.append('-n')
        [stat, _, _] = self.exec(*args)
        return stat == 0
