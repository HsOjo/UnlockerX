from app import Application
from app.shell import init_app_shell
from app.util.log import Log

app_shell = init_app_shell()
if app_shell.check():
    Log.init_app()

app = Application()

try:
    app.run()
except:
    app.callback_exception()
