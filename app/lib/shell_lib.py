from app import common


class ShellLib:
    def __init__(self, path):
        self.path = path

    def exec_out(self, *args):
        return common.execute_get_out([self.path, *args])

    def exec(self, *args):
        return common.execute([self.path, *args])
