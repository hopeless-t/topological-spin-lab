from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .provenance import Provenance
from .results import Exp001Result, Exp002Result
from .spec import Exp001Spec, spec_sha256
from .spec_exp002 import Exp002Spec


@dataclass(frozen=True, slots=True)
class EvidencePaths:
    manifest: Path
    metrics: Path
    spectrum: Path
    spin_ring: Path


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_evidence(
    spec: Exp001Spec | Exp002Spec,
    result: Exp001Result | Exp002Result,
    provenance: Provenance,
    output_dir: Path,
) -> EvidencePaths:
    """Serialize an existing result. This function performs no physics calculation."""
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    metrics_path = output_dir / "metrics.json"
    spectrum_path = output_dir / "spectrum.csv"
    spin_ring_path = output_dir / "spin_ring.csv"

    _write_json(
        manifest_path,
        {
            "experiment_id": spec.experiment_id,
            "schema_version": spec.schema_version,
            "spec_sha256": spec_sha256(spec),
            "status": result.status.value,
            "git_commit": provenance.git_commit,
            "python_version": provenance.python_version,
            "numpy_version": provenance.numpy_version,
            "platform": provenance.platform,
        },
    )

    _write_json(
        metrics_path,
        {
            "status": result.status.value,
            "metrics": asdict(result.metrics),
            "checks": [
                {
                    "name": check.name,
                    "observed": check.observed,
                    "limit": check.limit,
                    "unit": check.unit,
                    "passed": check.passed,
                }
                for check in result.checks
            ],
        },
    )

    with spectrum_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(result.spectrum[0]).keys()))
        writer.writeheader()
        for point in result.spectrum:
            writer.writerow(asdict(point))

    with spin_ring_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(result.spin_ring[0]).keys()))
        writer.writeheader()
        for point in result.spin_ring:
            writer.writerow(asdict(point))

    return EvidencePaths(
        manifest=manifest_path,
        metrics=metrics_path,
        spectrum=spectrum_path,
        spin_ring=spin_ring_path,
    )
