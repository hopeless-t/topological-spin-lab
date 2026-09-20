from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import scipy

from ..provenance import Provenance
from ..spec import spec_sha256
from ..spec_val001 import Val001Spec
from .val001 import Val001Result


@dataclass(frozen=True, slots=True)
class Val001EvidencePaths:
    manifest: Path
    summary: Path
    observations: Path
    method_summary: Path
    performance: Path


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_val001_evidence(
    spec: Val001Spec,
    result: Val001Result,
    provenance: Provenance,
    output_dir: Path,
) -> Val001EvidencePaths:
    """Serialize an existing VAL-001 result without rerunning eigensolves."""
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    summary_path = output_dir / "summary.json"
    observations_path = output_dir / "observations.csv"
    method_summary_path = output_dir / "method_summary.csv"
    performance_path = output_dir / "performance.json"

    _write_json(
        manifest_path,
        {
            "validation_id": spec.validation_id,
            "schema_version": spec.schema_version,
            "spec_sha256": spec_sha256(spec),
            "status": result.status.value,
            "git_commit": provenance.git_commit,
            "python_version": provenance.python_version,
            "numpy_version": provenance.numpy_version,
            "scipy_version": scipy.__version__,
            "platform": provenance.platform,
        },
    )

    _write_json(
        summary_path,
        {
            "status": result.status.value,
            "gates": [asdict(gate) for gate in result.gates],
            "method_summaries": [
                asdict(summary) for summary in result.method_summaries
            ],
            "decision": {
                "spectral_validator": result.spectral_validator,
                "best_wilson_r": result.best_wilson_r,
                "transport_candidate": result.transport_candidate,
                "transport_authorized": result.transport_authorized,
            },
        },
    )

    with observations_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(asdict(result.observations[0]).keys())
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for observation in result.observations:
            writer.writerow(asdict(observation))

    with method_summary_path.open("w", encoding="utf-8", newline="") as handle:
        rows: list[dict[str, object]] = []
        for summary in result.method_summaries:
            row = asdict(summary)
            row["failed_gates"] = ";".join(summary.failed_gates)
            row["profile_l1_by_grid"] = json.dumps(
                summary.profile_l1_by_grid,
                separators=(",", ":"),
            )
            rows.append(row)

        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    _write_json(
        performance_path,
        {
            "authority": "descriptive_noncanonical",
            "total_solver_seconds": result.total_solver_seconds,
            "note": (
                "Runtime is environment-dependent and is not used for "
                "VAL-001 PASS/FAIL."
            ),
        },
    )

    return Val001EvidencePaths(
        manifest=manifest_path,
        summary=summary_path,
        observations=observations_path,
        method_summary=method_summary_path,
        performance=performance_path,
    )
