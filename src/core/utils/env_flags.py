"""Helpers for interpreting boolean-like environment flags.

We centralize parsing to avoid common footguns such as `bool(os.environ.get(NAME))`
treating the string "0" as truthy.
"""


_FALSY_VALUES: set[str] = {"0", "false", "off", "no"}


def env_flag_enabled(env_value: str | None, *, default: bool = False) -> bool:
    """Interpret a boolean-like env flag value.

    Semantics (intentionally conservative and stable):

    - If the variable is unset (None) -> return `default`.
    - If the variable is set to an empty/whitespace string -> return `default`.
    - If the variable is set to an explicit falsy token (0/false/off/no) -> False.
    - Otherwise -> True.

    This avoids common footguns such as `bool(os.environ.get(NAME))` treating "0" as truthy.
    """

    if env_value is None:
        return default

    raw = env_value.strip()
    if raw == "":
        return default

    return raw.lower() not in _FALSY_VALUES
