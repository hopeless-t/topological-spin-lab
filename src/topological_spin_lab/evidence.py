from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .provenance import Provenance
from .results import Exp001Result, Exp002Result, Exp003Result
from .spec import Exp001Spec, spec_sha256
from .spec_exp002 import Exp002Spec
from .spec_exp003 import Exp003Spec


@dataclass(frozen=True, slots=True)
class EvidencePaths:
    manifest: Path
    metrics: Path
    spectrum: Path
    spin_ring: Path


@dataclass(frozen=True, slots=True)
class Exp003EvidencePaths:
    manifest: Path
    metrics: Path
    profile: Path
    dispersion: Path


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _manifest(
    spec: Exp001Spec | Exp002Spec | Exp003Spec,
    result: Exp001Result | Exp002Result | Exp003Result,
    provenance: Provenance,
) -> dict[str, object]:
    return {
        "experiment_id": spec.experiment_id,
        "schema_version": spec.schema_version,
        "spec_sha256": spec_sha256(spec),
        "status": result.status.value,
        "git_commit": provenance.git_commit,
        "python_version": provenance.python_version,
        "numpy_version": provenance.numpy_version,
        "platform": provenance.platform,
    }


def _metrics_payload(
    result: Exp001Result | Exp002Result | Exp003Result,
) -> dict[str, object]:
    return {
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
    }


def write_evidence(
    spec: Exp001Spec | Exp002Spec,
    result: Exp001Result | Exp002Result,
    provenance: Provenance,
    output_dir: Path,
) -> EvidencePaths:
    """Serialize an existing EXP-001/002 result without recalculating physics."""
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    metrics_path = output_dir / "metrics.json"
    spectrum_path = output_dir / "spectrum.csv"
    spin_ring_path = output_dir / "spin_ring.csv"

    _write_json(manifest_path, _manifest(spec, result, provenance))
    _write_json(metrics_path, _metrics_payload(result))

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


def write_exp003_evidence(
    spec: Exp003Spec,
    result: Exp003Result,
    provenance: Provenance,
    output_dir: Path,
) -> Exp003EvidencePaths:
    """Serialize an existing EXP-003 result without recalculating physics."""
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    metrics_path = output_dir / "metrics.json"
    profile_path = output_dir / "profile.csv"
    dispersion_path = output_dir / "dispersion.csv"

    _write_json(manifest_path, _manifest(spec, result, provenance))
    _write_json(metrics_path, _metrics_payload(result))

    with profile_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(result.profile[0]).keys()))
        writer.writeheader()
        for point in result.profile:
            writer.writerow(asdict(point))

    with dispersion_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(asdict(result.dispersion[0]).keys()),
        )
        writer.writeheader()
        for point in result.dispersion:
            writer.writerow(asdict(point))

    return Exp003EvidencePaths(
        manifest=manifest_path,
        metrics=metrics_path,
        profile=profile_path,
        dispersion=dispersion_path,
    )
