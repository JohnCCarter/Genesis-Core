import json
import statistics
from pathlib import Path

phase2_dir = Path("results/hparam_search/run_20251121_074845")
phase1_dir = Path("results/hparam_search/run_20251121_072643")
trial_files = sorted(phase2_dir.glob("trial_*.json"))
records = []
for tf in trial_files:
    try:
        data = json.loads(tf.read_text())
    except Exception:
        continue
    score_block = data.get("score")
    if isinstance(score_block, dict):
        numeric_score = score_block.get("score")
        metrics_block = score_block.get("metrics", {})
        trades = metrics_block.get("num_trades")
        return_pct = metrics_block.get("total_return")
        pf = metrics_block.get("profit_factor")
        max_dd = metrics_block.get("max_drawdown")
        sharpe = metrics_block.get("sharpe_ratio")
        win_rate = metrics_block.get("win_rate")
    else:
        numeric_score = None
        trades = None
        return_pct = None
        pf = None
        max_dd = None
        sharpe = None
        win_rate = None
    rec = {
        "score": numeric_score,
        "trades": trades,
        "return_pct": return_pct,
        "profit_factor": pf,
        "max_dd_pct": max_dd,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "constraints_ok": (
            data.get("constraints", {}).get("ok")
            if isinstance(data.get("constraints"), dict)
            else None
        ),
    }
    records.append(rec)
if not records:
    print("No phase2 trials found")
    raise SystemExit(1)
scores = [r["score"] for r in records if isinstance(r["score"], int | float)]
trades = [r["trades"] for r in records if isinstance(r["trades"], int | float)]
returns = [r["return_pct"] for r in records if isinstance(r["return_pct"], int | float)]
pfs = [r["profit_factor"] for r in records if isinstance(r["profit_factor"], int | float)]
dds = [r["max_dd_pct"] for r in records if isinstance(r["max_dd_pct"], int | float)]
wrates = [r["win_rate"] for r in records if isinstance(r["win_rate"], int | float)]
constraint_flags = [r["constraints_ok"] for r in records if isinstance(r["constraints_ok"], bool)]
metrics = {
    "total_trials": len(records),
    "avg_score": statistics.mean(scores),
    "best_score": max(scores),
    "median_score": statistics.median(scores),
    "avg_trades": statistics.mean(trades),
    "trade_rate_gt0": sum(1 for t in trades if t > 0) / len(trades),
    "avg_return_pct": statistics.mean(returns) if returns else None,
    "avg_profit_factor": statistics.mean(pfs) if pfs else None,
    "avg_max_dd_pct": statistics.mean(dds) if dds else None,
    "avg_win_rate": statistics.mean(wrates) if wrates else None,
    "constraints_ok_rate": (
        sum(1 for c in constraint_flags if c) / len(constraint_flags) if constraint_flags else None
    ),
    "score_stdev": statistics.pstdev(scores),
}
phase1_best = None
try:
    phase1_best = (
        json.loads((phase1_dir / "best_trial.json").read_text()).get("score", {}).get("score")
    )
except Exception:
    pass
metrics["phase1_best_score"] = phase1_best
if isinstance(phase1_best, int | float):
    metrics["best_score_delta_vs_phase1"] = metrics["best_score"] - phase1_best
out_path = phase2_dir / "phase2_metrics.json"
out_path.write_text(json.dumps(metrics, indent=2))
print("WROTE", out_path)
print(json.dumps(metrics, indent=2))
