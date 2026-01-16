from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


# Ensure repo root and src/ are importable when executing from scripts/.
# - repo root is needed for top-level helper modules like tools/*
# - src/ is needed for the actual project package (core/*)
_repo = _repo_root()
_src = _repo / "src"
for p in (str(_repo), str(_src)):
    if p not in sys.path:
        sys.path.insert(0, p)

from core.governance.registry import validate_registry  # noqa: E402
from tools.compare_backtest_results import (  # noqa: E402
    CompareResult,
    compare_backtest_payloads,
)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_jsonl_line(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def _last_nonempty_jsonl(path: Path) -> dict | None:
    if not path.exists():
        return None
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        return None
    try:
        obj = json.loads(lines[-1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _run_id(payload: dict) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:12]


def _priority_rank(compact: dict) -> int:
    val = compact.get("priority")
    if not isinstance(val, str):
        return 99
    mapping = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    return mapping.get(val, 99)


def _expand_compacts(
    *,
    compacts_by_key: dict[tuple[str, str], dict],
    roots: list[tuple[str, str]],
) -> list[tuple[tuple[str, str], dict]]:
    """Expand pack compacts (includes_compacts) recursively (small, bounded)."""

    out: list[tuple[tuple[str, str], dict]] = []
    seen: set[tuple[str, str]] = set()

    stack = list(roots)
    while stack:
        key = stack.pop()
        if key in seen:
            continue
        seen.add(key)

        compact = compacts_by_key.get(key)
        if compact is None:
            continue
        out.append((key, compact))

        includes = compact.get("includes_compacts")
        if isinstance(includes, list):
            for ref in includes:
                if not isinstance(ref, dict):
                    continue
                cid = str(ref.get("id", ""))
                ver = str(ref.get("version", ""))
                if cid and ver:
                    stack.append((cid, ver))

    return out


def _check_compact_conflicts(active: list[tuple[tuple[str, str], dict]]) -> list[str]:
    groups: dict[str, list[tuple[int, str]]] = {}
    for (cid, ver), compact in active:
        cg = compact.get("conflict_group")
        if not isinstance(cg, str) or not cg.strip():
            continue
        label = f"{cid}@{ver}"
        groups.setdefault(cg, []).append((_priority_rank(compact), label))

    errors: list[str] = []
    for cg, items in groups.items():
        if len(items) <= 1:
            continue
        items_sorted = sorted(items, key=lambda x: (x[0], x[1]))
        keep = items_sorted[0][1]
        others = [lbl for _, lbl in items_sorted[1:]]
        errors.append(
            f"compact conflict in group {cg!r}: {[lbl for _, lbl in items_sorted]}. "
            f"Alternative A: keep {keep} and remove {others}. "
            f"Alternative B: remove {keep} and keep one of {others}."
        )
    return errors


def _resolve_registry(manifest: str) -> tuple[dict, dict[str, dict], dict[str, dict]]:
    root = _repo_root()
    manifest_path = root / "registry" / "manifests" / f"{manifest}.json"
    manifest_obj = _load_json(manifest_path)
    if not isinstance(manifest_obj, dict):
        raise ValueError(f"manifest must be a JSON object: {manifest_path}")

    skills: dict[str, dict] = {}
    for p in (root / ".github" / "skills").glob("*.json"):
        obj = _load_json(p)
        if isinstance(obj, dict) and isinstance(obj.get("id"), str):
            skills[obj["id"]] = obj

    compacts: dict[str, dict] = {}
    for p in (root / "registry" / "compacts").glob("*.json"):
        obj = _load_json(p)
        if isinstance(obj, dict) and isinstance(obj.get("id"), str):
            compacts[obj["id"]] = obj

    return manifest_obj, skills, compacts


def _audit_emit(
    *,
    audit_path: Path,
    run_id: str,
    skill_id: str,
    skill_version: str,
    manifest: str,
    stage: str,
    status: str,
    details: dict,
    dry_run: bool,
    dedupe: bool,
) -> None:
    entry = {
        "run_id": run_id,
        "skill": {"id": skill_id, "version": skill_version},
        "manifest": manifest,
        "stage": stage,
        "status": status,
        "details": details,
    }

    print(f"[AUDIT] {stage}: {status}")

    if dry_run:
        return

    if dedupe:
        last = _last_nonempty_jsonl(audit_path)
        if last and last.get("run_id") == run_id and last.get("stage") == "Result":
            return

    _write_jsonl_line(audit_path, entry)


def _step_registry_validate() -> tuple[bool, dict]:
    result = validate_registry(_repo_root())
    if result.ok:
        return True, {"ok": True}
    return False, {"ok": False, "errors": result.errors}


def _step_compare_backtests(*, baseline_path: Path, candidate_path: Path) -> tuple[bool, dict]:
    baseline = _load_json(baseline_path)
    candidate = _load_json(candidate_path)

    cmp: CompareResult = compare_backtest_payloads(
        baseline=baseline, candidate=candidate, mode="strict"
    )
    ok = cmp.status == "PASS"
    return ok, {
        "status": cmp.status,
        "failure": cmp.failure,
        "failures": cmp.failures,
        "deltas": cmp.deltas,
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skill", required=True, help="Skill id")
    p.add_argument("--manifest", required=True, choices=["dev", "stable"])
    p.add_argument("--baseline", default=None, help="Override baseline backtest path")
    p.add_argument("--candidate", default=None, help="Override candidate backtest path")
    p.add_argument("--audit-file", default="logs/skill_runs.jsonl")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--audit-dedupe", action=argparse.BooleanOptionalAction, default=True)
    args = p.parse_args(argv)

    audit_path = _repo_root() / args.audit_file

    manifest_obj, skills_by_id, compacts_by_id = _resolve_registry(args.manifest)

    # Resolve requested skill version via manifest.
    skill_ref = None
    for ref in (
        manifest_obj.get("skills", []) if isinstance(manifest_obj.get("skills"), list) else []
    ):
        if isinstance(ref, dict) and ref.get("id") == args.skill:
            skill_ref = ref
            break

    if not isinstance(skill_ref, dict):
        print(f"[SKILL] STOP: skill {args.skill!r} is not present in manifest {args.manifest!r}")
        return 3

    skill_version = str(skill_ref.get("version", ""))
    skill = skills_by_id.get(args.skill)
    if not skill or str(skill.get("version")) != skill_version:
        print(f"[SKILL] FAIL: registry skill definition missing for {args.skill}@{skill_version}")
        return 1

    # Resolve compacts referenced by manifest.
    compact_keys: list[tuple[str, str]] = []
    compacts_by_key: dict[tuple[str, str], dict] = {}

    for c in compacts_by_id.values():
        cid = str(c.get("id", ""))
        ver = str(c.get("version", ""))
        if cid and ver:
            compacts_by_key[(cid, ver)] = c

    for ref in (
        manifest_obj.get("compacts", []) if isinstance(manifest_obj.get("compacts"), list) else []
    ):
        if not isinstance(ref, dict):
            continue
        cid = str(ref.get("id", ""))
        ver = str(ref.get("version", ""))
        if cid and ver:
            compact_keys.append((cid, ver))

    active_compacts = _expand_compacts(compacts_by_key=compacts_by_key, roots=compact_keys)
    conflict_errors = _check_compact_conflicts(active_compacts)

    run_payload = {
        "skill": args.skill,
        "skill_version": skill_version,
        "manifest": args.manifest,
        "baseline": args.baseline,
        "candidate": args.candidate,
        "compact_keys": sorted([f"{cid}@{ver}" for (cid, ver), _ in active_compacts]),
    }
    run_id = _run_id(run_payload)

    _audit_emit(
        audit_path=audit_path,
        run_id=run_id,
        skill_id=args.skill,
        skill_version=skill_version,
        manifest=args.manifest,
        stage="Triggered",
        status="OK",
        details={"compacts": run_payload["compact_keys"]},
        dry_run=args.dry_run,
        dedupe=args.audit_dedupe,
    )

    if conflict_errors:
        _audit_emit(
            audit_path=audit_path,
            run_id=run_id,
            skill_id=args.skill,
            skill_version=skill_version,
            manifest=args.manifest,
            stage="Verified",
            status="STOP",
            details={"reason": "compact_conflict", "errors": conflict_errors},
            dry_run=args.dry_run,
            dedupe=args.audit_dedupe,
        )
        _audit_emit(
            audit_path=audit_path,
            run_id=run_id,
            skill_id=args.skill,
            skill_version=skill_version,
            manifest=args.manifest,
            stage="Result",
            status="STOP",
            details={"reason": "compact_conflict"},
            dry_run=args.dry_run,
            dedupe=args.audit_dedupe,
        )
        print("[SKILL] STOP: compact conflicts detected")
        for e in conflict_errors:
            print(f"- {e}")
        return 3

    steps = skill.get("steps")
    if not isinstance(steps, list) or not steps:
        _audit_emit(
            audit_path=audit_path,
            run_id=run_id,
            skill_id=args.skill,
            skill_version=skill_version,
            manifest=args.manifest,
            stage="Verified",
            status="STOP",
            details={"reason": "no_steps"},
            dry_run=args.dry_run,
            dedupe=args.audit_dedupe,
        )
        _audit_emit(
            audit_path=audit_path,
            run_id=run_id,
            skill_id=args.skill,
            skill_version=skill_version,
            manifest=args.manifest,
            stage="Result",
            status="STOP",
            details={"reason": "no_steps"},
            dry_run=args.dry_run,
            dedupe=args.audit_dedupe,
        )
        print("[SKILL] STOP: skill has no executable steps")
        return 3

    _audit_emit(
        audit_path=audit_path,
        run_id=run_id,
        skill_id=args.skill,
        skill_version=skill_version,
        manifest=args.manifest,
        stage="Verified",
        status="OK",
        details={},
        dry_run=args.dry_run,
        dedupe=args.audit_dedupe,
    )

    for step in steps:
        if not isinstance(step, dict):
            print("[SKILL] FAIL: invalid step")
            return 1
        stype = step.get("type")
        sargs = step.get("args") if isinstance(step.get("args"), dict) else {}

        if stype == "registry_validate":
            ok, detail = _step_registry_validate()
        elif stype == "compare_backtest_results":
            baseline = args.baseline or sargs.get("baseline_path")
            candidate = args.candidate or sargs.get("candidate_path")
            if not isinstance(baseline, str) or not isinstance(candidate, str):
                ok, detail = False, {"reason": "missing_paths"}
            else:
                ok, detail = _step_compare_backtests(
                    baseline_path=_repo_root() / baseline,
                    candidate_path=_repo_root() / candidate,
                )
        else:
            ok, detail = False, {"reason": f"unknown_step_type:{stype!r}"}

        if not ok:
            _audit_emit(
                audit_path=audit_path,
                run_id=run_id,
                skill_id=args.skill,
                skill_version=skill_version,
                manifest=args.manifest,
                stage="Result",
                status="FAIL",
                details={"step": step.get("id"), **detail},
                dry_run=args.dry_run,
                dedupe=args.audit_dedupe,
            )
            print("[SKILL] FAIL")
            return 1

    _audit_emit(
        audit_path=audit_path,
        run_id=run_id,
        skill_id=args.skill,
        skill_version=skill_version,
        manifest=args.manifest,
        stage="Result",
        status="PASS",
        details={},
        dry_run=args.dry_run,
        dedupe=args.audit_dedupe,
    )

    print("[SKILL] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
