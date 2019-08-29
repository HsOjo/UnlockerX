from app import common
from app.util import log


class ObjectConvertor:
    @staticmethod
    def _to_basic(o: object, constant):
        if constant:
            return o
        elif isinstance(o, int) or isinstance(o, float):
            r = str(o)
        elif isinstance(o, bool):
            r = str(o).lower()
        else:
            r = '"%s"' % str(o).replace('\n', '\\n').replace('"', '\\"')
        return r

    @staticmethod
    def _to_list(l: list, constant):
        r = ''
        for i in l:
            if r != '':
                r += ', '
            r += ObjectConvertor.to_object(i, constant)
        return '{%s}' % r

    @staticmethod
    def _to_dict(d: dict, constant):
        r = ''
        for k, v in d.items():
            if r != '':
                r += ', '
            r += '%s: %s' % (k, ObjectConvertor.to_object(v, constant))
        return '{%s}' % r

    @staticmethod
    def to_object(o: object, constant=False):
        if isinstance(o, list):
            r = ObjectConvertor._to_list(o, constant)
        elif isinstance(o, dict):
            r = ObjectConvertor._to_dict(o, constant)
        else:
            r = ObjectConvertor._to_basic(o, constant)

        return r


class AppleScript:
    @staticmethod
    def exec(code: str, timeout=None):
        stat, out, err = common.execute('/usr/bin/osascript', code, timeout)
        log.append(AppleScript.exec, 'AppleScript', locals())
        return stat, out, err
