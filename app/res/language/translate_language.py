import json
import os

from app.util import pyinstaller, object_convert
from app.util.log import Log
from tools.translate import Translator
from .english import English


class TranslateLanguage(English):
    _resource_name = ''
    _translate_by = English
    _translate_from = 'en'
    _translate_to = ''
    _replace_words = {}

    def __init__(self):
        self._data_path = '%s/app/res/language/translate/%s.json' % (
            pyinstaller.get_runtime_dir(), self._resource_name[self._resource_name.rfind('.') + 1:])
        self._translated = self.load_local_translate()

    def load_local_translate(self):
        if os.path.exists(self._data_path):
            try:
                with open(self._data_path, 'r', encoding='utf-8') as io:
                    language = json.load(io)
                object_convert.dict_to_object(language, self, False)
                return True
            except:
                pass

        return False

    def save_current_translate(self):
        language = object_convert.object_to_dict(self)
        with open(self._data_path, 'w', encoding='utf-8') as io:
            json.dump(language, io, ensure_ascii=False, indent=4)

    def translate(self, t: Translator):
        def replace(text):
            for i, c in self._replace_words.items():
                text = text.replace(i, c)
            return text

        def translate(text):
            _text = text
            text = replace(text)
            text = t.translate(self._translate_from, self._translate_to, text)
            text = replace(text)
            Log.append(self.translate, 'Translate', '\n%s\n%s' % (_text, text))
            return text

        for k in dir(self._translate_by):
            if k[0] != '_' and k != 'l_this':
                v = getattr(self._translate_by, k)
                if isinstance(v, str):
                    setattr(self, k, translate(v))
                elif isinstance(v, dict):
                    v = v.copy()
                    for kk, vv in v.items():
                        v[kk] = translate(vv)
                    setattr(self, k, v)
