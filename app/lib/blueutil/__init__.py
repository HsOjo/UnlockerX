from app import common


class BlueUtil:
    def __init__(self, path):
        self.path = path

    @property
    def power(self):
        content = common.execute_get_out('%s --power' % self.path)
        return bool(int(content))

    @power.setter
    def power(self, power: bool):
        common.execute('%s --power %s' % (self.path, int(power)))

    @property
    def discoverable(self):
        content = common.execute_get_out('%s --discoverable' % self.path)
        return bool(int(content))

    @discoverable.setter
    def discoverable(self, discoverable: bool):
        common.execute('%s --discoverable %s' % (self.path, int(discoverable)))

    def convert_device(self, content):
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
                item['signal_value'] = int(cols[1][cols[1].find('-'):cols[1].find('dBm')].strip())

        return item

    def convert_devices(self, content: str):
        result = []
        for line in content.split('\n'):
            if line.strip() != '':
                result.append(self.convert_device(line))

        return result

    def inquiry(self, time=10):
        return self.convert_devices(common.execute_get_out('%s --inquiry %s' % (self.path, time)))

    def recent(self, num=10):
        return self.convert_devices(common.execute_get_out('%s --recent %s' % (self.path, num)))

    @property
    def favourites(self):
        return self.convert_devices(common.execute_get_out('%s --favourites' % (self.path)))

    @property
    def paired(self):
        return self.convert_devices(common.execute_get_out('%s --paired' % (self.path)))

    def info(self, dev_id: str):
        return self.convert_device(common.execute_get_out('%s --info %s' % (self.path, dev_id)))

    def is_connected(self, dev_id: str):
        content = common.execute_get_out('%s --is-connected %s' % (self.path, dev_id))
        return bool(int(content))

    def connect(self, dev_id: str):
        stat, out, err = common.execute('%s --connect %s' % (self.path, dev_id))
        return stat == 0

    def pair(self, dev_id: str, pin=''):
        stat, out, err = common.execute('%s --pair %s %s' % (self.path, dev_id, pin))
        return stat == 0
