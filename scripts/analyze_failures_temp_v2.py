import glob
import json
import os
from collections import Counter


def analyze():
    # Try a broader glob first to ensure we catch everything
    path = os.path.join("results", "hparam_search", "run_20251208_091646", "*.json")
    files = glob.glob(path)
    c = Counter()

    print(f"Found {len(files)} files in total.")

    processed = 0
    for f in files:
        # Skip metadata files
        if "run_meta.json" in f or "trial_001_config.json" in f:
            continue

        try:
            with open(f) as fd:
                content = fd.read()
                if not content.strip():
                    continue
                d = json.loads(content)

            processed += 1

            # Debug first file
            if processed == 1:
                print(f"DEBUG: First file {f} keys: {list(d.keys())}")
                if "constraints" in d:
                    print(f"DEBUG: Constraints: {d['constraints']}")
                if "error" in d:
                    print(f"DEBUG: Error: {d['error']}")

            found_reason = False

            # Check constraints
            constraints = d.get("constraints", {})
            if constraints and isinstance(constraints, dict):
                reasons = constraints.get("reasons", [])
                if reasons:
                    for r in reasons:
                        c[r] += 1
                    found_reason = True

            # Check errors
            if not found_reason and d.get("error"):
                c[f"Error: {d.get('error')}"] += 1
                found_reason = True

            # Check hard failures in score
            if not found_reason and d.get("score", {}).get("hard_failures"):
                for r in d["score"]["hard_failures"]:
                    c[f"Hard Fail: {r}"] += 1
                found_reason = True

            if not found_reason:
                # Maybe it's a success? or empty?
                if "metrics" in d or "score" in d:
                    c["Unknown/Success?"] += 1
                else:
                    c["Empty/Invalid"] += 1

        except Exception as e:
            print(f"Failed to read {f}: {e}")

    print("\nFailure Reasons Summary:")
    print("-" * 30)
    for reason, count in c.most_common():
        print(f"{count:3d} trials: {reason}")


if __name__ == "__main__":
    analyze()
