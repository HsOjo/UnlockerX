class Translator:
    lang_code = {}

    def __init__(self):
        self.buffer = {}
        self.use_buffer = False

    def set_use_buffer(self, b):
        self.use_buffer = b

    def get_buffer(self, lang_from, lang_to, content):
        key = '%s->%s' % (lang_from, lang_to)

        buffer = self.buffer.get(key)  # type: dict
        if buffer is None:
            return None

        return buffer.get(content)

    def set_buffer(self, lang_from, lang_to, content, translate):
        key = '%s->%s' % (lang_from, lang_to)

        buffer = self.buffer.get(key)  # type: dict
        if buffer is None:
            self.buffer[key] = {}

        buffer = self.buffer[key]
        buffer[content] = translate

    def _translate(self, lang_from, lang_to, content):
        pass

    def translate(self, lang_from, lang_to, content):
        lang_from = self.lang_code.get(lang_from, lang_from)
        lang_to = self.lang_code.get(lang_to, lang_to)

        if self.use_buffer:
            translate = self.get_buffer(lang_from, lang_to, content)
            if translate is not None:
                return translate

        translate = self._translate(lang_from, lang_to, content)

        if self.use_buffer:
            self.set_buffer(lang_from, lang_to, content, translate)

        return translate
