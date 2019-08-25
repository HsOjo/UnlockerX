from zhconv import convert

from .translator import Translator


class ZHConv(Translator):
    lang_code = {
        'cn': 'zh-cn',
        'cn_t': 'zh-hant',
    }

    def _translate(self, lang_from, lang_to, content):
        return convert(content, lang_to)
