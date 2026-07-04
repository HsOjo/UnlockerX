from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

from app.res.const import Const


@dataclass
class Release:
    name: str
    tag_name: str
    published_at: str
    html_url: str
    body: str
    download_url: Optional[str]


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
    url = f'https://api.github.com/repos/{Const.author}/{Const.app_name}/releases/latest'
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    download_url = None
    assets = data.get('assets') or []
    if assets:
        download_url = assets[0].get('browser_download_url')

    return Release(
        name=data.get('name', ''),
        tag_name=data.get('tag_name', ''),
        published_at=data.get('published_at', '').replace('T', ' ').replace('Z', ''),
        html_url=data.get('html_url', Const.releases_url),
        body=data.get('body', ''),
        download_url=download_url,
    )


def check_update(timeout: float = 5) -> tuple[Optional[Release], bool]:
    """Fetch the latest release and whether it is newer than the running version.

    Returns (release, have_new). Raises on network/parse errors.
    """
    release = get_latest_release(timeout=timeout)
    return release, compare_version(Const.version, release.tag_name)
