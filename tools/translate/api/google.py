import re
import time
from traceback import print_exc

import requests

from .translator import Translator


class GoogleTranslate(Translator):
    lang_code = {
        'cn': 'zh-cn',
        'jp': 'ja',
    }

    def __init__(self):
        super().__init__()

    def __translate(self, lang_from, lang_to, content):
        if content.strip() == '':
            return content

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        session = requests.session()

        resp = session.get('https://translate.google.cn/', headers=headers)
        [tkk] = re.findall(r"tkk:'([\d\\.]*)'", resp.text)

        from execjs import eval as js_eval
        tk = js_eval('''
function _(a,TKK) {
var b = function (a, b) {
  for (var d = 0; d < b.length - 2; d += 3) {
    var c = b.charAt(d + 2),
      c = "a" <= c ? c.charCodeAt(0) - 87 : Number(c),
      c = "+" === b.charAt(d + 1) ? a >>> c : a << c;
    a = "+" === b.charAt(d) ? a + c & 4294967295 : a ^ c
  }
  return a
};
  for (var e = TKK.split("."), h = Number(e[0]) || 0, g = [], d = 0, f = 0; f < a.length; f++) {
    var c = a.charCodeAt(f);
    128 > c ? g[d++] = c : (2048 > c ? g[d++] = c >> 6 | 192 : (55296 === (c & 64512) && f + 1 < a.length && 56320 === (a.charCodeAt(f + 1) & 64512) ? (c = 65536 + ((c & 1023) << 10) + (a.charCodeAt(++f) & 1023), g[d++] = c >> 18 | 240, g[d++] = c >> 12 & 63 | 128) : g[d++] = c >> 12 | 224, g[d++] = c >> 6 & 63 | 128), g[d++] = c & 63 | 128)
  }
  a = h;
  for (d = 0; d < g.length; d++) a += g[d], a = b(a, "+-a^+6");
  a = b(a, "+-3^+b+-f");
  a ^= Number(e[1]) || 0;
  0 > a && (a = (a & 2147483647) + 2147483648);
  a %= 1E6;
  return a.toString() + "." + (a ^ h)
} 
''' + '("%s","%s")' % (content.replace('\n', '\\n').replace('"', '\\"'), tkk))

        params = {
            'client': 'webapp',
            'sl': lang_from,
            'tl': lang_to,
            'hl': lang_to,
            'q': content,
            'tk': tk,
            'otf': 2,
            'ssel': 0,
            'tsel': 0,
            'kc': 1,
        }

        result = None
        for i in range(5):
            try:
                resp = session.get(
                    'https://translate.google.cn/translate_a/single?dt=at&dt=bd&dt=ex&dt=ld&dt=md&dt=qca&dt=rw&dt=rm&dt=ss&dt=t&ie=UTF-8&oe=UTF-8',
                    params=params, headers=headers, timeout=10)
                result = resp.json()[0][0][0]
                break
            except:
                time.sleep(1)

        if result is None:
            raise Exception('Translate failed.')

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
