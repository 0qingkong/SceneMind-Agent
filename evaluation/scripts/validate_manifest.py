from __future__ import annotations

import argparse
from pathlib import Path

from evaluation.scripts.common import ROOT, ensure_relative_reference, read_csv, read_jsonl


ALLOWED_LICENSES = {"synthetic-team-owned", "team-owned", "explicit-permission", "public-licensed"}


def validate_scenes(path: Path, require_assets: bool = False) -> list[str]:
    errors: list[str] = []
    rows = read_jsonl(path)
    seen: set[str] = set()
    for index, row in enumerate(rows, 1):
        sample_id = str(row.get("sample_id", "")).strip()
        if not sample_id:
            errors.append(f"row {index}: missing sample_id")
        elif sample_id in seen:
            errors.append(f"row {index}: duplicate sample_id {sample_id}")
        seen.add(sample_id)
        if row.get("license") not in ALLOWED_LICENSES:
            errors.append(f"row {index}: invalid permission/license")
        asset_path = str(row.get("asset_path") or "")
        asset_key = str(row.get("asset_key") or "")
        if not asset_path and not asset_key:
            errors.append(f"row {index}: asset_path or asset_key is required")
        if asset_path:
            try:
                ensure_relative_reference(asset_path)
            except ValueError as exc:
                errors.append(f"row {index}: {exc}")
            if require_assets and not (ROOT / asset_path).is_file():
                errors.append(f"row {index}: missing asset {asset_path}")
    return errors


def validate_relations(path: Path) -> list[str]:
    required = {"sample_id", "observation_id", "subject_label", "predicate", "object_label", "predicted", "manual_correct", "ambiguous", "reviewer_note"}
    rows = read_csv(path)
    if not rows:
        return ["relation annotations are empty"]
    missing = required - set(rows[0])
    errors = [f"missing relation columns: {sorted(missing)}"] if missing else []
    for index, row in enumerate(rows, 2):
        if not row.get("sample_id") or not row.get("observation_id"):
            errors.append(f"row {index}: sample_id and observation_id are required")
        if not row.get("subject_label") or not row.get("object_label"):
            errors.append(f"row {index}: subject and object labels are required")
        if row.get("subject_label") == row.get("object_label"):
            errors.append(f"row {index}: self-relations are invalid")
        if row.get("predicted", "").casefold() not in {"true", "false"}:
            errors.append(f"row {index}: predicted must be true/false")
        if row.get("manual_correct", "").casefold() not in {"true", "false"}:
            errors.append(f"row {index}: manual_correct must be true/false")
        if row.get("ambiguous", "").casefold() not in {"true", "false"}:
            errors.append(f"row {index}: ambiguous must be true/false")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenes", type=Path, default=ROOT / "evaluation/manifests/scenes.example.jsonl")
    parser.add_argument("--relations", type=Path, default=ROOT / "evaluation/manifests/relation_annotations.example.csv")
    parser.add_argument("--require-assets", action="store_true")
    args = parser.parse_args()
    errors = validate_scenes(args.scenes, args.require_assets) + validate_relations(args.relations)
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        raise SystemExit(1)
    print("PASS evaluation manifests are valid")


if __name__ == "__main__":
    main()
