"""Regression tests for MCP stdio encoding hardening.

The MCP stdio transport writes JSON responses to stdout. On Windows, some hosts
default to legacy encodings (e.g. cp1252), which can crash on non-ASCII output.
"""

from __future__ import annotations


def test_ensure_utf8_stdio_calls_reconfigure(monkeypatch):
    from mcp_server import server as mcp_server

    calls: list[tuple[str, str]] = []

    class _FakeStream:
        def reconfigure(self, *, encoding: str, errors: str) -> None:
            calls.append((encoding, errors))

    fake_stdout = _FakeStream()
    fake_stderr = _FakeStream()

    monkeypatch.setattr(mcp_server.sys, "stdout", fake_stdout)
    monkeypatch.setattr(mcp_server.sys, "stderr", fake_stderr)

    mcp_server._ensure_utf8_stdio()

    assert calls == [("utf-8", "strict"), ("utf-8", "strict")]
