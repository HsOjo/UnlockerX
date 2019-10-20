import json
import os

from .baidu import BaiduTranslate
from .google import GoogleTranslate
from .translator import Translator
from .zhconv import ZHConv

CONFIG_FILE = './tools/translate/config.json'

config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as io:
        config = json.load(io)


def baidu_translate(appid=None, key=None):
    if appid is None or key is None:
        return BaiduTranslate(**config.get('baidu'))
    else:
        return BaiduTranslate(appid, key)


def google_translate():
    return GoogleTranslate()


def zhconv():
    return ZHConv()
