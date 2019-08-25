LANGUAGES = {}


class Language:
    unknown = '? ? ?: (%s)'

    def __getattr__(self, key):
        if key not in dir(self):
            if '%s' in self.unknown:
                return self.unknown % key
            else:
                return self.unknown


def load_language(code='en'):
    from .english import English
    from .chinese import Chinese
    from .chinese_t import TraditionalChinese
    from .japanese import Japanese
    from .korean import Korean

    LANGUAGES['en'] = English
    LANGUAGES['cn'] = Chinese
    LANGUAGES['cn_t'] = TraditionalChinese
    LANGUAGES['jp'] = Japanese
    LANGUAGES['ko'] = Korean

    language = LANGUAGES.get(code, English)()  # type: English
    return language
