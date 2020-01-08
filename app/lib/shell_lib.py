from app import common


class ShellLib:
    def __init__(self, path):
        self.path = path

    def exec_out(self, *args, **kwargs):
        return common.execute_get_out([self.path, *args], **kwargs)

    def exec(self, *args, **kwargs):
        return common.execute([self.path, *args], **kwargs)

    def popen(self, *args, **kwargs):
        return common.popen([self.path, *args], **kwargs)
