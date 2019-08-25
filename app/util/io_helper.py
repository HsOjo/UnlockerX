from io import StringIO


def read_all(io: StringIO, default=None):
    if io is not None:
        io.seek(0)
        content = io.read()
        io.seek(0, 2)
    else:
        content = default
    return content
