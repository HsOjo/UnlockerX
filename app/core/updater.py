from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

from app.res.const import Const


@dataclass
class Release:
    name: str
    tag_name: str
    published_at: str
    html_url: str
    body: str


def _norm_version(version: str) -> list[int]:
    """Convert a version string to a list of integers for lexicographic compare.

    Strips leading 'v'/'V' and ignores pre-release tags (anything after '-').
    Non-numeric parts are treated as 0 so malformed segments don't abort.
    """
    v = (version or '').lstrip('vV').split('-')[0]
    parts = []
    for part in v.split('.'):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return parts


def compare_version(current: str, latest: str) -> bool:
    """Return True if `latest` is strictly newer than `current`.

    Pre-release tags (containing '-') are ignored.
    """
    if '-' in latest:
        return False
    a, b = _norm_version(current), _norm_version(latest)
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return b > a


def get_latest_release(timeout: float = 5) -> Release:
    """Parse the latest release from the GitHub releases HTML page.

    GitHub's REST API has a very low unauthenticated rate limit (60 req/hour),
    so we scrape the public releases page instead.
    """
    resp = requests.get(Const.releases_url, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    tag_link = soup.find(
        'a',
        href=re.compile(rf'^/{Const.author}/{Const.app_name}/releases/tag/'),
    )
    if not tag_link:
        raise ValueError('Could not find release tag on GitHub releases page')

    href = tag_link.get('href', '')
    tag_name = href.split('/')[-1]
    html_url = f'https://github.com{href}'
    name = tag_link.text.strip()

    published_at = ''
    body = ''
    section = tag_link.find_parent('section')
    if section:
        time_tag = section.find('relative-time')
        if time_tag:
            published_at = (time_tag.get('datetime') or '').replace('T', ' ').replace('Z', '')
        body_tag = section.find('div', class_='markdown-body')
        if body_tag:
            body = body_tag.get_text('\n').strip()

    return Release(
        name=name,
        tag_name=tag_name,
        published_at=published_at,
        html_url=html_url,
        body=body,
    )


def check_update(timeout: float = 5) -> tuple[Optional[Release], bool]:
    """Fetch the latest release and whether it is newer than the running version.

    Returns (release, have_new). Raises on network/parse errors.
    """
    release = get_latest_release(timeout=timeout)
    return release, compare_version(Const.version, release.tag_name)
