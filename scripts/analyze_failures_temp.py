import glob
import json
import os
from collections import Counter


def analyze():
    path = os.path.join(
        "results", "hparam_search", "run_20251208_091646", "tBTCUSD_1h_trial_*.json"
    )
    files = glob.glob(path)
    c = Counter()

    print(f"Analyzing {len(files)} files...")

    for f in files:
        try:
            with open(f) as fd:
                d = json.load(fd)

            # Check constraints
            constraints = d.get("constraints", {})
            reasons = constraints.get("reasons", [])

            if reasons:
                for r in reasons:
                    c[r] += 1

            # Check errors
            elif d.get("error"):
                c[f"Error: {d.get('error')}"] += 1

            # Check hard failures in score if no explicit constraint reasons
            elif d.get("score", {}).get("hard_failures"):
                for r in d["score"]["hard_failures"]:
                    c[f"Hard Fail: {r}"] += 1

        except Exception as e:
            print(f"Failed to read {f}: {e}")

    print("\nFailure Reasons Summary:")
    print("-" * 30)
    for reason, count in c.most_common():
        print(f"{count:3d} trials: {reason}")


if __name__ == "__main__":
    analyze()
