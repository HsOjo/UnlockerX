from .chinese import Chinese
from .translate_language import TranslateLanguage


class TraditionalChinese(TranslateLanguage):
    _resource_name = __name__
    _translate_by = Chinese
    _translate_from = 'cn'
    _translate_to = 'cn_t'
    _replace_words = {
        '文件': '档案',
        '设置': '设定',
        '显示器': '显示幕',
        '磁盘': '磁碟',
        '内存': '记忆体',
        '模式': '范式',
    }

    l_this = '繁體中文'
