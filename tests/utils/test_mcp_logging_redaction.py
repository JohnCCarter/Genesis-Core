from __future__ import annotations

from mcp_server.utils import safe_args_for_logging


def test_safe_args_redacts_content_and_code_for_write_and_execute_tools():
    args = {"content": "secret text", "code": "print('x')", "other": "value"}

    write_redacted = safe_args_for_logging("write_file", args)
    exec_redacted = safe_args_for_logging("execute_python", args)

    assert write_redacted["content"] == "<redacted len=11>"
    assert write_redacted["code"] == "<redacted len=10>"
    assert write_redacted["other"] == "value"

    assert exec_redacted["content"] == "<redacted len=11>"
    assert exec_redacted["code"] == "<redacted len=10>"
    assert exec_redacted["other"] == "value"


def test_safe_args_keeps_non_sensitive_tools_unchanged():
    args = {"query": "hello", "pr_body": "body"}

    result = safe_args_for_logging("search", args)

    assert result == args


def test_safe_args_redacts_pr_body_only_when_enabled_for_git_tools():
    args = {"pr_body": "sensitive pr body", "title": "keep"}

    default_result = safe_args_for_logging("git_create_pr", args)
    enabled_result = safe_args_for_logging("git_create_pr", args, redact_pr_body=True)

    assert default_result["pr_body"] == "sensitive pr body"
    assert enabled_result["pr_body"] == "<redacted len=17>"
    assert default_result["title"] == "keep"
    assert enabled_result["title"] == "keep"


def test_safe_args_uses_na_for_non_string_redacted_values():
    args = {"content": 123, "code": None, "pr_body": 456}

    result = safe_args_for_logging("git_workflow", args, redact_pr_body=True)
    write_result = safe_args_for_logging("write_file", args)

    assert write_result["content"] == "<redacted len=n/a>"
    assert write_result["code"] == "<redacted len=n/a>"
    assert result["pr_body"] == "<redacted len=n/a>"
