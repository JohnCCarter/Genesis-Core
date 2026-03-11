from __future__ import annotations


def test_log_precompute_status_logs_once_and_flips_state() -> None:
    import core.strategy.features_asof as features_asof

    class _FakeLogger:
        def __init__(self) -> None:
            self.calls = []

        def debug(self, message, *args) -> None:
            self.calls.append((message, args))

    original_logger = features_asof._log
    original_once = features_asof._PRECOMPUTE_DEBUG_ONCE
    fake_logger = _FakeLogger()
    try:
        features_asof._log = fake_logger
        features_asof._PRECOMPUTE_DEBUG_ONCE = False

        features_asof._log_precompute_status(True, {"b": 2, "a": 1}, 7, 3)
        features_asof._log_precompute_status(False, {"z": 1}, 8, 4)

        assert features_asof._PRECOMPUTE_DEBUG_ONCE is True
        assert len(fake_logger.calls) == 1
        message, args = fake_logger.calls[0]
        assert message == (
            "precompute_status use_precompute=%s lookup_idx=%s window_start_idx=%s pre_keys=%s"
        )
        assert args == (True, 7, 3, ["a", "b"])
    finally:
        features_asof._log = original_logger
        features_asof._PRECOMPUTE_DEBUG_ONCE = original_once


def test_log_precompute_status_keeps_state_when_logger_missing() -> None:
    import core.strategy.features_asof as features_asof

    original_logger = features_asof._log
    original_once = features_asof._PRECOMPUTE_DEBUG_ONCE
    try:
        features_asof._log = None
        features_asof._PRECOMPUTE_DEBUG_ONCE = False

        features_asof._log_precompute_status(True, {"a": 1}, 7, 3)

        assert features_asof._PRECOMPUTE_DEBUG_ONCE is False
    finally:
        features_asof._log = original_logger
        features_asof._PRECOMPUTE_DEBUG_ONCE = original_once
