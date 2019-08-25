import shutil
import sys
from zipfile import ZipFile

from app.res.const import Const
from app.res.language import load_language, LANGUAGES
from app.res.language.translate_language import TranslateLanguage
from app.util import log
from tools.translate import *

datas = {}


def add_data(src, dest):
    datas[src] = dest


# build translate language data.
log.append('Build', 'Info', 'Building translate data now...')
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
            log.append('Build', 'Translate', 'Using %s' % translator.__class__.__name__)

            lang.translate(translator)
            lang.save_current_translate()
        add_data(lang._data_path, './app/res/language/translate')

# reset dist directory.
shutil.rmtree('./build', ignore_errors=True)
shutil.rmtree('./dist', ignore_errors=True)

add_data('./app/res/icon.png', './app/res')

data_str = ''
for k, v in datas.items():
    data_str += ' \\\n\t'
    data_str += '--add-data "%s:%s"' % (k, v)

log.append('Build', 'Info', 'Pyinstaller packing now...')
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

log.append('Build', 'Info', 'Packing release zip file now...')

# pack release zip file.
zf = ZipFile('./dist/%s-%s.zip' % (Const.app_name, Const.version), 'w')
src_dir = './dist/%s.app' % Const.app_name
for d, ds, fs in os.walk(src_dir):
    for f in fs:
        path = os.path.join(d, f)
        z_path = path[7:].strip(os.path.sep)
        zf.write(path, z_path)
zf.close()

log.append('Build', 'Info', 'Build finish.')
