from app import common


class BlueUtil:
    def __init__(self, path):
        self.path = path

    def _exec_out(self, *args):
        return common.execute_get_out([self.path, *args])

    def _exec(self, *args):
        return common.execute([self.path, *args])

    def _convert_device(self, content):
        cols = content.split(',')

        item = {}
        if len(cols) > 2:
            if '(' in cols[1]:
                for i in cols[2:]:
                    cols.remove(i)
                    cols[1] += i
                    if ')' in i:
                        break
            item = {
                'address': cols[0][cols[0].find(':') + 1:].strip(),
                'is_connected': 'not' not in cols[1],
                'is_favourite': 'not' not in cols[2],
                'is_paired': 'not' not in cols[3],
                'name': cols[4][cols[4].find('"') + 1:cols[4].rfind('"')].strip(),
                'recent_access_date': cols[5][cols[5].find(':') + 1:].strip(),
            }

            if item['is_connected']:
                value_str = cols[1][cols[1].find('-'):cols[1].find('dBm')].strip()
                if value_str.replace('-', '', 1).isnumeric():
                    item['signal_value'] = int(value_str)

        return item

    def _convert_devices(self, content: str):
        result = []
        for line in content.split('\n'):
            if line.strip() != '':
                result.append(self._convert_device(line))

        return result

    @property
    def power(self):
        content = self._exec_out('--power')
        return bool(int(content))

    @power.setter
    def power(self, power: bool):
        self._exec_out('--power', str(int(power)))

    @property
    def discoverable(self):
        content = self._exec_out('--discoverable')
        return bool(int(content))

    @discoverable.setter
    def discoverable(self, discoverable: bool):
        self._exec_out('--discoverable', str(int(discoverable)))

    def inquiry(self, time=10):
        return self._convert_devices(self._exec_out('--inquiry', str(int(time))))

    def recent(self, num=10):
        return self._convert_devices(self._exec_out('--recent', str(int(num))))

    @property
    def favourites(self):
        return self._convert_devices(self._exec_out('--favourites'))

    @property
    def paired(self):
        return self._convert_devices(self._exec_out('--paired'))

    def info(self, dev_id: str):
        return self._convert_device(self._exec_out('--info', dev_id))

    def is_connected(self, dev_id: str):
        content = self._exec_out('--is-connected', dev_id)
        return bool(int(content))

    def connect(self, dev_id: str):
        stat, out, err = self._exec('--connect', dev_id)
        return stat == 0

    def pair(self, dev_id: str, pin=''):
        stat, out, err = self._exec('--pair', dev_id, pin)
        return stat == 0
