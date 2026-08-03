from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
for candidate in (str(ROOT), str(BACKEND)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{number}: invalid JSON") from exc
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: Iterable[float], quantile: float) -> float | None:
    ordered = sorted(float(item) for item in values)
    if not ordered:
        return None
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * quantile
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def latency_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    data = [float(item) for item in values]
    return {
        "count": len(data),
        "min_ms": round(min(data), 3) if data else None,
        "p50_ms": round(percentile(data, 0.5), 3) if data else None,
        "p95_ms": round(percentile(data, 0.95), 3) if data else None,
        "max_ms": round(max(data), 3) if data else None,
        "mean_ms": round(statistics.fmean(data), 3) if data else None,
    }


def safe_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def environment(analyzer_mode: str, model: str | None) -> dict[str, object]:
    try:
        import torch
        pytorch_version = torch.__version__
        cuda_available: bool | None = bool(torch.cuda.is_available())
        cuda_device_count: int | None = int(torch.cuda.device_count())
    except Exception as exc:
        pytorch_version = f"unavailable ({type(exc).__name__})"
        cuda_available = None
        cuda_device_count = None
    try:
        import ultralytics
        ultralytics_version = ultralytics.__version__
    except Exception as exc:
        ultralytics_version = f"unavailable ({type(exc).__name__})"

    try:
        import psutil
        memory_gib: float | None = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        memory_gib = None
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit": safe_commit(),
        "os": platform.system(),
        "architecture": platform.machine(),
        "logical_cpu_count": os.cpu_count(),
        "memory_gib": memory_gib,
        "python": platform.python_version(),
        "node": _command_version(["node", "--version"]),
        "pytorch": pytorch_version,
        "ultralytics": ultralytics_version,
        "cuda_available": cuda_available,
        "cuda_device_count": cuda_device_count,
        "analyzer_mode": analyzer_mode,
        "model_identifier": Path(model).name if model else "none",
    }


def _command_version(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unavailable"


def ensure_relative_reference(value: str) -> None:
    if not value:
        return
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.drive:
        raise ValueError(f"asset reference must be relative: {value}")


def no_absolute_paths(payload: object) -> bool:
    encoded = json.dumps(payload, ensure_ascii=False)
    forbidden = [str(ROOT), str(Path.home()), os.environ.get("USERPROFILE", "")]
    return all(not item or item not in encoded for item in forbidden)
