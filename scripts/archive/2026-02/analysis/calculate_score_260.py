#!/usr/bin/env python3
"""Beräkna vad score=260 betyder i termer av metrics."""

import numpy as np

print("=== Champion Score 260.73 - Analys ===\n")
print("Champion metrics:")
sharpe = 0.0
total_return = 0.10427224105362948
max_dd = 0.0
win_rate = 0.34666666666666673
print(f"  Sharpe: {sharpe}")
print(f"  Total Return: {total_return*100:.2f}%")
print(f"  Max Drawdown: {max_dd*100:.2f}% (NOL!)")
print(f"  Win Rate: {win_rate*100:.1f}%\n")

print("Score-beräkning:")
ret_ratio = total_return / max(0.0001, max_dd if max_dd > 0 else 0.0001)
win_rate_contrib = np.clip(win_rate - 0.4, -0.2, 0.2)
base_score = sharpe + total_return + (ret_ratio * 0.25) + win_rate_contrib
print(f"  return_to_dd = {total_return} / max(0.0001, {max_dd}) = {ret_ratio:.2f}")
print(f"  win_rate_clip = clip({win_rate} - 0.4, -0.2, 0.2) = {win_rate_contrib:.3f}")
print(
    f"  base_score = {sharpe} + {total_return:.6f} + ({ret_ratio:.2f} * 0.25) + {win_rate_contrib:.3f}"
)
print(f"  base_score = {base_score:.2f}\n")

print("=== Vad krävs för score=260? ===\n")
target = 260

print("Scenario 1: Med max_dd=0.0 (som champion):")
ret_ratio_needed = (target - sharpe - total_return - win_rate_contrib) / 0.25
max_dd_needed = total_return / ret_ratio_needed
print(f"  Om Return={total_return*100:.2f}%, Win Rate={win_rate*100:.1f}%:")
print(f"  Krävs return_to_dd: {ret_ratio_needed:.2f}")
print(f"  Med Return={total_return*100:.2f}% → Max DD måste vara: {max_dd_needed*100:.4f}%")
print(f"  (Praktiskt: max_dd < 0.0001% ger return_to_dd > {total_return/0.0001:.0f})\n")

print("Scenario 2: Med realistisk max_dd (t.ex. 1%):")
max_dd_real = 0.01
ret_ratio_real = total_return / max_dd_real
score_real = sharpe + total_return + (ret_ratio_real * 0.25) + win_rate_contrib
print(f"  Om Return={total_return*100:.2f}%, Max DD={max_dd_real*100:.1f}%:")
print(f"  return_to_dd = {ret_ratio_real:.2f}")
print(f"  Score = {score_real:.2f}")
needed_return = target - sharpe - win_rate_contrib - (ret_ratio_real * 0.25)
print(f"  För score=260 krävs Return: {needed_return:.2f} (omöjligt!)\n")

print("=== Jämförelse: Champion vs Parity Test ===\n")
print("Champion (score=260.73):")
print(f"  Return: {total_return*100:.2f}%, Max DD: {max_dd*100:.2f}%, Return/DD: {ret_ratio:.0f}")
print(f"  Score: {base_score:.2f}\n")

print("Parity Test (score=0.5865):")
parity_return = 0.0596
parity_dd = 0.0329
parity_sharpe = 0.067
parity_win = 0.407
parity_ret_ratio = parity_return / parity_dd
parity_win_contrib = np.clip(parity_win - 0.4, -0.2, 0.2)
parity_score = parity_sharpe + parity_return + (parity_ret_ratio * 0.25) + parity_win_contrib
print(
    f"  Return: {parity_return*100:.2f}%, Max DD: {parity_dd*100:.2f}%, Return/DD: {parity_ret_ratio:.2f}"
)
print(f"  Score: {parity_score:.2f}\n")

print("=== Slutsats ===")
print("Score=260 kräver antingen:")
print("  1. max_drawdown ≈ 0.0% (som champion) → return_to_dd blir extremt hög")
print("  2. Championens score=260.73 är p.g.a. max_dd=0.0 (ingen drawdown!)")
print("  3. Med realistisk max_dd (1-5%) är score=260 praktiskt omöjligt")
print("  4. Championens score är artificiellt hög p.g.a. max_dd=0.0 bugg/avrundning")
