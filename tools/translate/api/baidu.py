import time
from hashlib import md5
from traceback import print_exc

import requests

from .translator import Translator


class BaiduTranslate(Translator):
    lang_code = {
        'cn': 'zh',
        'ko': 'kor',
    }

    def __init__(self, appid, key):
        super().__init__()
        self.appid = appid
        self.key = key

    def __translate(self, lang_from, lang_to, content):
        if content.strip() == '':
            return content

        url = 'http://fanyi-api.baidu.com/api/trans/vip/translate'
        salt = 0
        sign = md5((self.appid + content + str(salt) + self.key).encode('utf-8')).hexdigest()
        param = {
            'q': content,
            'from': lang_from,
            'to': lang_to,
            'appid': self.appid,
            'salt': salt,
            'sign': sign,
        }

        while True:
            try:
                resp = requests.get(url, params=param, timeout=5)
                result = resp.json()['trans_result'][0]['dst']
                break
            except Exception as e:
                time.sleep(1)

        return result

    def _translate(self, lang_from, lang_to, content):
        ret = ''
        lines = content.split('\n')
        for line in lines:
            while True:
                try:
                    if self.use_buffer:
                        line_t = self.get_buffer(lang_from, lang_to, line)
                        if line_t is not None:
                            line_t = self.__translate(lang_from, lang_to, line)
                        self.set_buffer(lang_from, lang_to, line, line_t)
                    else:
                        line_t = self.__translate(lang_from, lang_to, line)

                    if ret != '':
                        ret += '\n'
                    ret += line_t
                    break
                except:
                    print_exc()
                    time.sleep(1)

        return ret
