from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.experiments.exp002 import execute_exp002
from topological_spin_lab.spec import spec_sha256
from topological_spin_lab.spec_exp002 import Exp002Spec

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "EXP-002.json"
REFERENCE_DIR = ROOT / "evidence" / "EXP-002" / "reference"


def _csv_rows(name: str) -> list[dict[str, str]]:
    with (REFERENCE_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _spec() -> Exp002Spec:
    spec = load_any_experiment_spec(SPEC_PATH)
    assert isinstance(spec, Exp002Spec)
    return spec


def test_exp002_reference_manifest_matches_current_contract() -> None:
    spec = _spec()
    manifest = json.loads((REFERENCE_DIR / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((REFERENCE_DIR / "metrics.json").read_text(encoding="utf-8"))

    assert manifest["experiment_id"] == spec.experiment_id
    assert manifest["schema_version"] == spec.schema_version
    assert manifest["spec_sha256"] == spec_sha256(spec)
    assert manifest["status"] == "PASS"
    assert metrics["status"] == "PASS"
    assert len(metrics["checks"]) == 11
    assert all(check["passed"] for check in metrics["checks"])


def test_exp002_reference_observation_grids_are_complete() -> None:
    spec = _spec()
    spectrum = _csv_rows("spectrum.csv")
    spin_ring = _csv_rows("spin_ring.csv")

    assert len(spectrum) == spec.sampling.spectrum.points
    assert len(spin_ring) == spec.sampling.spin_ring.angles * 2
    assert {row["band"] for row in spin_ring} == {"lower", "upper"}


def test_exp002_reference_physical_sanity() -> None:
    spec = _spec()
    spectrum = _csv_rows("spectrum.csv")
    spin_ring = _csv_rows("spin_ring.csv")

    zero = min(spectrum, key=lambda row: abs(float(row["kx_Ainv"])))
    observed_gap = float(zero["upper_eV"]) - float(zero["lower_eV"])
    assert math.isclose(
        observed_gap,
        2.0 * abs(spec.model.mass_eV),
        rel_tol=0.0,
        abs_tol=spec.acceptance.direct_gap_abs_eV,
    )

    upper_sz = [float(row["sz"]) for row in spin_ring if row["band"] == "upper"]
    lower_sz = [float(row["sz"]) for row in spin_ring if row["band"] == "lower"]
    assert all(value > 0.0 for value in upper_sz)
    assert all(value < 0.0 for value in lower_sz)


def test_current_exp002_stays_within_reference_tolerances() -> None:
    spec = _spec()
    result = execute_exp002(spec)

    reference_spectrum = _csv_rows("spectrum.csv")
    assert len(reference_spectrum) == len(result.spectrum)

    spectrum_atol = spec.acceptance.analytic_spectrum_abs_eV
    for current, reference in zip(result.spectrum, reference_spectrum, strict=True):
        np.testing.assert_allclose(
            [current.kx_Ainv, current.ky_Ainv],
            [float(reference["kx_Ainv"]), float(reference["ky_Ainv"])],
            rtol=0.0,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            [current.lower_eV, current.upper_eV],
            [float(reference["lower_eV"]), float(reference["upper_eV"])],
            rtol=0.0,
            atol=spectrum_atol,
        )

    reference_spin = _csv_rows("spin_ring.csv")
    assert len(reference_spin) == len(result.spin_ring)

    spin_atol = max(
        spec.acceptance.spin_norm_abs,
        spec.acceptance.spin_momentum_dot_abs,
        spec.acceptance.spin_vector_abs,
        spec.acceptance.helicity_abs,
        spec.acceptance.center_spin_abs,
    )
    for current, reference in zip(result.spin_ring, reference_spin, strict=True):
        assert current.band == reference["band"]
        np.testing.assert_allclose(
            [current.angle_rad, current.kx_Ainv, current.ky_Ainv],
            [
                float(reference["angle_rad"]),
                float(reference["kx_Ainv"]),
                float(reference["ky_Ainv"]),
            ],
            rtol=0.0,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            [current.sx, current.sy, current.sz, current.helicity],
            [
                float(reference["sx"]),
                float(reference["sy"]),
                float(reference["sz"]),
                float(reference["helicity"]),
            ],
            rtol=0.0,
            atol=spin_atol,
        )
