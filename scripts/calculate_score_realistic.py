#!/usr/bin/env python3
"""
Beräkna realistisk mål-score för Phase 3.
Ersätter den gamla 'score 260'-analysen som baserades på 0.00% drawdown.

Nytt Mål (High Quality Swing):
- Win Rate: > 50% (User request: "mer winrate")
- Profit Factor: > 1.3
- Max Drawdown: < 10%
- Return: > 15%
"""

import numpy as np


def calculate_score(sharpe, total_return, max_dd, win_rate):
    # Samma formel som i src/core/optimizer/scoring.py
    ret_ratio = total_return / max(0.0001, max_dd if max_dd > 0 else 0.0001)

    # Win rate contribution (current logic)
    # Rewards WR > 40%, penalties WR < 40%
    # Max reward at 60% WR (+0.2)
    win_rate_contrib = np.clip(win_rate - 0.4, -0.2, 0.2)

    base_score = sharpe
    base_score += total_return
    base_score += ret_ratio * 0.25
    base_score += win_rate_contrib

    return base_score


print("=== REALISTISK MÅL-ANALYS (Phase 3) ===\n")

scenarios = [
    {
        "name": "Nuvarande Bästa (Trial 11)",
        "sharpe": 0.058,
        "return": 0.1077,
        "dd": 0.0484,
        "wr": 0.533,
    },
    {"name": "Mål: Balanserad (Realistic)", "sharpe": 1.0, "return": 0.15, "dd": 0.08, "wr": 0.50},
    {
        "name": "Mål: High Win Rate (User Pref)",
        "sharpe": 1.5,
        "return": 0.15,
        "dd": 0.05,
        "wr": 0.60,
    },
    {"name": "Drömscenario (Perfect)", "sharpe": 2.0, "return": 0.25, "dd": 0.05, "wr": 0.65},
]

for s in scenarios:
    score = calculate_score(s["sharpe"], s["return"], s["dd"], s["wr"])
    print(f"Scenario: {s['name']}")
    print(f"  Return: {s['return']*100:.1f}%")
    print(f"  Max DD: {s['dd']*100:.1f}%")
    print(f"  Win Rate: {s['wr']*100:.1f}%")
    print(f"  Sharpe: {s['sharpe']:.2f}")
    print(f"  -> SCORE: {score:.4f}")
    print("-" * 30)

print("\nSlutsats:")
print("En score över 1.50 är ett mycket bra resultat.")
print("En score över 2.00 är exceptionellt.")
print("Det gamla målet på 260 var baserat på en matematisk singularitet (DD=0).")
