from .chinese import Chinese
from .translate_language import TranslateLanguage


class Korean(TranslateLanguage):
    _resource_name = __name__
    _translate_by = Chinese
    _translate_from = 'cn'
    _translate_to = 'ko'
    _replace_words = {
        '% ': '%',
        ':%': ': %',
        '%1 s': '%s',
    }

    l_this = '한국어'
