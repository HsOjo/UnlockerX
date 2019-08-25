import html
import re

import requests

from app import common


def html_to_plain_text(content):
    content = html.unescape(content)

    reg_br = re.compile('</?br/?>')
    for i in reg_br.findall(content):
        content = content.replace(i, '\n')

    reg_tags = re.compile('</?.*?/?>')
    for t in reg_tags.findall(content):
        content = content.replace(t, '')

    p_content = ''
    while p_content != content:
        p_content = content
        content = content.replace('\n\n', '\n')
    content = content.strip()

    return content


def url_jump(url: str, link):
    if '://' in link:
        return link
    elif link[0] == '/':
        p = url.find('/', url.find('://') + 3)
        return '%s%s' % (url[:p], link)
    else:
        return '%s/%s' % (url, link)


def convert_datetime(text):
    reg = re.compile('(.*?)T(.*?)Z')
    [item] = reg.findall(text)
    return ' '.join(item)


def get_releases(url, **kwargs):
    resp = requests.get(url, **kwargs)
    resp_str = resp.content.decode('utf-8')

    reg = re.compile('<div class="release-entry">[\s\S]*?<!-- /.release -->\s*</div>')
    releases = reg.findall(resp_str)

    reg_head = re.compile('<div class="d-flex flex-items-start">[\s\S]*?<a href="(.*)">(.*)</a>')
    reg_date_time = re.compile('<relative-time datetime="(.*?)">.*</relative-time>')
    reg_content = re.compile('<div class="markdown-body">([\s\S]*?)</div>')

    result = []
    for r in releases:
        link, title = common.reg_find_one(reg_head, r)
        dt_text = common.reg_find_one(reg_date_time, r)
        item = {
            'url': url_jump(resp.url, link),
            'title': title,
            'datetime': convert_datetime(dt_text),
            'description': html_to_plain_text(common.reg_find_one(reg_content, r)),
        }
        result.append(item)

    return result


def get_latest_release(user, repo, **kwargs):
    url = 'https://api.github.com/repos/%s/%s/releases/latest' % (user, repo)

    resp = requests.get(url, **kwargs)
    resp_data = resp.json()  # type: dict

    release = {
        'html_url': resp_data['html_url'],
        'created_at': convert_datetime(resp_data['published_at']),
        'published_at': convert_datetime(resp_data['published_at']),
        'tag_name': resp_data['tag_name'],
        'name': resp_data['name'],
        'body': resp_data['body'],
        'assets': [],
    }

    for asset in resp_data['assets']:
        release['assets'].append({
            'name': asset['name'],
            'size': asset['size'],
            'created_at': convert_datetime(asset['created_at']),
            'updated_at': convert_datetime(asset['updated_at']),
            'browser_download_url': asset['browser_download_url'],
        })

    return release
