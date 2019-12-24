import shutil
import sys
from zipfile import ZipFile

from app import Log
from app.res.const import Const
from app.res.language import load_language, LANGUAGES
from app.res.language.translate_language import TranslateLanguage
from tools.translate import *
from tools.utils.zip import zip_directory

datas = {}


def add_data(src, dest):
    if os.path.exists(src):
        datas[src] = dest


# build translate language data.
Log.append('Build', 'Info', 'Building translate data now...')
load_language()
for lang_type in LANGUAGES.values():
    if issubclass(lang_type, TranslateLanguage):
        lang = lang_type()
        if not lang._translated:
            if lang._translate_to == 'cn_t':
                translator = zhconv()
            elif '--translate-baidu' in sys.argv:
                translator = baidu_translate()
            else:
                translator = google_translate()
            Log.append('Build', 'Translate', 'Using %s' % translator.__class__.__name__)

            lang.translate(translator)
            lang.save_current_translate()
        add_data(lang._data_path, './app/res/language/translate')

# reset dist directory.
shutil.rmtree('./build', ignore_errors=True)
shutil.rmtree('./dist', ignore_errors=True)

add_data('./app/res/icon.png', './app/res')
add_data('./app/res/icon_weak_signal.png', './app/res')
add_data('./app/res/icon_disconnect.png', './app/res')
add_data('./app/res/icon.png', './app/res')
add_data('./app/lib/blueutil/blueutil', './app/lib/blueutil')
add_data('./app/lib/bluetoothconnector/BluetoothConnector', './app/lib/bluetoothconnector')

path_app_dir = './dist/%s.app' % Const.app_name
path_app_zip = './dist/%s-%s.zip' % (Const.app_name, Const.version)

use_py2app = '--py2app' in sys.argv
if use_py2app:
    Log.append('Build', 'Info', 'Py2App packing now...')
    os.system('python setup.py py2app')
    shutil.rmtree('./build', ignore_errors=True)

    res_dir = '%s/Contents/Resources' % path_app_dir
    for f, fd in datas.items():
        dd = ('%s/%s' % (res_dir, fd)).replace('/./', '/')
        os.makedirs(dd, exist_ok=True)
        shutil.copy(f, dd)

    # clean not .pyc files.
    Log.append('Build', 'Info', 'Cleaning...')
    lib_dir = '%s/lib' % res_dir
    [lib_file] = [f for f in os.listdir(lib_dir) if 'python' in f and '.zip' in f]
    lib_path = '%s/%s' % (lib_dir, lib_file)
    with ZipFile(lib_path, 'r') as zf:
        zf.extractall(lib_file)

    zip_directory(lib_file, lib_path, filter_='(.*\.pyc$)|(.*\.pem$)', remove='.*__pycache__.*')
    shutil.rmtree(lib_file)
else:
    data_str = ''
    for k, v in datas.items():
        data_str += ' \\\n\t'
        data_str += '--add-data "%s:%s"' % (k, v)

    Log.append('Build', 'Info', 'Pyinstaller packing now...')
    pyi_cmd = 'pyinstaller -F -w -n "%s" -i "./app/res/icon.icns" %s \\\n__main__.py' % (Const.app_name, data_str)
    print(pyi_cmd)
    os.system(pyi_cmd)
    os.unlink('./%s.spec' % Const.app_name)
    shutil.rmtree('./build', ignore_errors=True)

    # hide dock icon.
    INFO_FILE = './dist/%s.app/Contents/Info.plist' % Const.app_name

    with open(INFO_FILE, 'r') as io:
        info = io.read()

    dict_pos = info.find('<dict>') + 7
    info = info[:dict_pos] + '\t<key>LSUIElement</key>\n\t<string>1</string>\n' + info[dict_pos:]
    with open(INFO_FILE, 'w') as io:
        io.write(info)

# pack release zip file.
Log.append('Build', 'Info', 'Packing release zip file now...')
zip_directory(path_app_dir, path_app_zip, remove='.*__pycache__.*', dirname=True)
Log.append('Build', 'Info', 'Build finish.')
