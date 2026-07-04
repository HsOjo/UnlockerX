"""Tests for process helpers."""

from __future__ import annotations

from app.platform import proc


def test_run_returns_output():
    rc, out, err = proc.run(['/bin/echo', 'hello'])
    assert rc == 0
    assert out.strip() == 'hello'


def test_run_reports_timeout():
    rc, out, err = proc.run(['/bin/sleep', '10'], timeout=0.1)
    assert rc == -1
