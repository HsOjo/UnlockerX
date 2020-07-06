import json

from app.lib.shell_lib import ShellLib


class DeviceInfo:
    def __init__(self, data: dict):
        self._data = data

    @property
    def name(self) -> str:
        return self._data.get('name')

    @property
    def address(self) -> str:
        return self._data.get('address')

    @property
    def recent_access_date(self) -> str:
        return self._data.get('recentAccessDate')

    @property
    def is_paired(self) -> bool:
        return self._data.get('paired', False)

    @property
    def is_favourite(self) -> bool:
        return self._data.get('favourite', False)

    @property
    def is_connected(self) -> bool:
        return self._data.get('connected', False)

    @property
    def is_slave(self) -> bool:
        return self._data.get('slave', False)

    @property
    def rssi(self) -> int:
        return self._data.get('RSSI')

    @property
    def raw_rssi(self) -> int:
        return self._data.get('rawRSSI')

    @property
    def raw_data(self) -> dict:
        return self._data

    def __repr__(self):
        return '%s:%s' % (super(DeviceInfo, self).__repr__(), self._data.__repr__())


class BlueUtil(ShellLib):
    @staticmethod
    def _convert_device(data):
        if isinstance(data, dict):
            return DeviceInfo(data)
        else:
            return None

    @staticmethod
    def _convert_devices(devices):
        result = []
        try:
            for device in devices:
                result.append(BlueUtil._convert_device(device))
        except:
            pass
        return result

    def exec_out(self, *args, **kwargs):
        args = list(args)
        args.append('--format')
        args.append('json')
        result = super().exec_out(*args, **kwargs)
        return json.loads(result)

    @property
    def power(self):
        content = self.exec_out('--power')
        return bool(content)

    def set_power(self, b: bool):
        self.exec_out('--power', str(int(b)))

    @property
    def discoverable(self):
        content = self.exec_out('--discoverable')
        return bool(content)

    def set_discoverable(self, b: bool):
        self.exec_out('--discoverable', str(int(b)))

    def inquiry(self, time=10):
        return self._convert_devices(self.exec_out('--inquiry', str(int(time))))

    def recent(self, num=10):
        return self._convert_devices(self.exec_out('--recent', str(int(num))))

    @property
    def favourites(self):
        return self._convert_devices(self.exec_out('--favourites'))

    @property
    def paired(self):
        return self._convert_devices(self.exec_out('--paired'))

    def info(self, dev_id: str):
        return self._convert_device(self.exec_out('--info', dev_id))

    def is_connected(self, dev_id: str):
        content = self.exec_out('--is-connected', dev_id)
        return bool(content)

    def connect(self, dev_id: str):
        stat, out, err = self.exec('--connect', dev_id)
        return stat == 0

    def pair(self, dev_id: str, pin=''):
        stat, out, err = self.exec('--pair', dev_id, pin)
        return stat == 0
