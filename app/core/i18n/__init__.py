from __future__ import annotations

LANGUAGES = {}


class Language:
    """Base i18n class.

    Missing attributes degrade to a visible placeholder instead of crashing,
    which makes adding new strings to one language at a time safe.
    """

    code = 'en'
    l_this = 'English'

    def unknown(self, key):
        return f'? ? ?: ({key})'

    def __getattr__(self, key):
        # __getattr__ is only called for missing attributes; guard against
        # infinite recursion for methods that exist on the class/object.
        if key in dir(self):
            return None
        # Missing translation methods (e.g. view_device_nane) should raise
        # AttributeError so typos are caught, not silently return a placeholder.
        if key.startswith('_') or key.startswith(('view_', 'noti_update_', 'unknown')):
            raise AttributeError(key)
        return self.unknown(key)


def _register():
    from .english import English
    from .chinese import Chinese
    from .chinese_t import TraditionalChinese
    from .japanese import Japanese
    from .korean import Korean

    LANGUAGES.clear()
    LANGUAGES['en'] = English
    LANGUAGES['cn'] = Chinese
    LANGUAGES['cn_t'] = TraditionalChinese
    LANGUAGES['jp'] = Japanese
    LANGUAGES['ko'] = Korean


def load_language(code='en'):
    """Return a language instance for the requested code."""
    if not LANGUAGES:
        _register()
    from .english import English
    return LANGUAGES.get(code, English)()


# Keep the existing UnlockerX API name as a thin alias.
def get_language(code: str) -> Language:
    return load_language(code)


def map_locale(locale_code: str) -> str:
    """Map an NSLocale-style identifier to one of our 5 supported codes."""
    if not locale_code:
        return 'en'
    c = locale_code.replace('_', '-').lower()
    if c.startswith('zh'):
        if 'hant' in c or 'tw' in c or 'hk' in c or 'mo' in c:
            return 'cn_t'
        return 'cn'
    if c.startswith('ja'):
        return 'jp'
    if c.startswith('ko'):
        return 'ko'
    return 'en'
