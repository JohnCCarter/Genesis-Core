from __future__ import annotations

from scripts.optimizer import _analyze_param_synergy, _flatten_scalar_params


def test_flatten_scalar_params_keeps_only_scalars() -> None:
    params = {
        "thresholds": {"entry_conf_overall": 0.25, "mode": "x"},
        "exit": {"enabled": True, "risk_map": [[0.5, 0.01]]},
        "nested": {"a": {"b": {"c": 1}}},
        "none_value": None,
    }

    flat = _flatten_scalar_params(params)

    assert flat["thresholds.entry_conf_overall"] == 0.25
    assert flat["thresholds.mode"] == "x"
    assert flat["exit.enabled"] is True
    assert flat["nested.a.b.c"] == 1

    # non-scalars are intentionally skipped
    assert "exit.risk_map" not in flat
    assert "none_value" not in flat


def test_analyze_param_synergy_finds_pair_interaction() -> None:
    # Create a simple 2x2 interaction:
    # scores are best when a=1 and b=1, with lift beyond best single.
    valid_trials = []
    for a in (0, 1):
        for b in (0, 1):
            for _rep in range(3):
                score = 5.0
                if a == 1:
                    score += 1.0
                if b == 1:
                    score += 1.0
                if a == 1 and b == 1:
                    score += 3.0

                valid_trials.append(
                    {
                        "trial_id": f"t_{a}_{b}",
                        "score": score,
                        "parameters": {"p": {"a": a, "b": b}},
                        "metrics": {"num_trades": 10},
                    }
                )

    singles, pairs, _numeric_edges = _analyze_param_synergy(
        valid_trials,
        top_params=2,
        bins=4,
        min_count=2,
        top_pairs=10,
    )

    assert singles
    assert pairs

    # Expect top pair to be p.a + p.b with best bin combination representing a=1, b=1.
    top = pairs[0]
    assert {top.param_a, top.param_b} == {"p.a", "p.b"}
    assert top.best_median > 8.0
    assert top.best_count >= 2
    assert top.synergy_vs_best_single > 0.0
