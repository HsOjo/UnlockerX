from app.res.language.english import English


class ViewBase:
    def __init__(self):
        self.lang = None  # type: English

    def add_menu(self, name, title='', callback=None, parent=None):
        pass
