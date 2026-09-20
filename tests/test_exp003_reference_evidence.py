from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from topological_spin_lab.experiment_loader import load_any_experiment_spec
from topological_spin_lab.experiments.exp003 import execute_exp003
from topological_spin_lab.spec import spec_sha256
from topological_spin_lab.spec_exp003 import Exp003Spec

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "specs" / "EXP-003.json"
REFERENCE_DIR = ROOT / "evidence" / "EXP-003" / "reference"


def _csv_rows(name: str) -> list[dict[str, str]]:
    with (REFERENCE_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _spec() -> Exp003Spec:
    spec = load_any_experiment_spec(SPEC_PATH)
    assert isinstance(spec, Exp003Spec)
    return spec


def test_exp003_reference_manifest_matches_current_contract() -> None:
    spec = _spec()
    manifest = json.loads((REFERENCE_DIR / "manifest.json").read_text(encoding="utf-8"))
    metrics = json.loads((REFERENCE_DIR / "metrics.json").read_text(encoding="utf-8"))

    assert manifest["experiment_id"] == spec.experiment_id
    assert manifest["schema_version"] == spec.schema_version
    assert manifest["spec_sha256"] == spec_sha256(spec)
    assert manifest["status"] == "PASS"
    assert metrics["status"] == "PASS"
    assert len(metrics["checks"]) == 10
    assert all(check["passed"] for check in metrics["checks"])


def test_exp003_reference_grids_and_physical_sanity() -> None:
    spec = _spec()
    profile = _csv_rows("profile.csv")
    dispersion = _csv_rows("dispersion.csv")

    assert len(profile) == spec.sampling.profile.points == 241
    assert len(dispersion) == spec.sampling.dispersion.points == 101

    center = min(profile, key=lambda row: abs(float(row["x_A"])))
    peak = max(float(row["probability_density_Ainv"]) for row in profile)
    assert math.isclose(float(center["x_A"]), 0.0, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(
        float(center["mass_eV"]),
        0.0,
        rel_tol=0.0,
        abs_tol=spec.acceptance.mass_center_abs_eV,
    )
    assert math.isclose(
        float(center["probability_density_Ainv"]),
        peak,
        rel_tol=0.0,
        abs_tol=spec.acceptance.density_symmetry_abs_Ainv,
    )

    negative = dispersion[0]
    zero = min(dispersion, key=lambda row: abs(float(row["ky_Ainv"])))
    positive = dispersion[-1]

    assert float(negative["energy_eV"]) < 0.0
    assert math.isclose(
        float(zero["energy_eV"]),
        0.0,
        rel_tol=0.0,
        abs_tol=spec.acceptance.dispersion_abs_eV,
    )
    assert float(positive["energy_eV"]) > 0.0
    assert all(float(row["binding_margin_eV"]) > 0.0 for row in dispersion)


def test_current_exp003_stays_within_reference_tolerances() -> None:
    spec = _spec()
    result = execute_exp003(spec)

    reference_profile = _csv_rows("profile.csv")
    assert len(reference_profile) == len(result.profile)

    for current, reference in zip(result.profile, reference_profile, strict=True):
        np.testing.assert_allclose(
            current.x_A,
            float(reference["x_A"]),
            rtol=0.0,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            current.mass_eV,
            float(reference["mass_eV"]),
            rtol=0.0,
            atol=spec.acceptance.mass_center_abs_eV,
        )
        np.testing.assert_allclose(
            current.probability_density_Ainv,
            float(reference["probability_density_Ainv"]),
            rtol=0.0,
            atol=spec.acceptance.density_symmetry_abs_Ainv,
        )

    reference_dispersion = _csv_rows("dispersion.csv")
    assert len(reference_dispersion) == len(result.dispersion)

    for current, reference in zip(result.dispersion, reference_dispersion, strict=True):
        np.testing.assert_allclose(
            current.ky_Ainv,
            float(reference["ky_Ainv"]),
            rtol=0.0,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            [
                current.energy_eV,
                current.analytic_energy_eV,
                current.bulk_edge_abs_eV,
                current.binding_margin_eV,
            ],
            [
                float(reference["energy_eV"]),
                float(reference["analytic_energy_eV"]),
                float(reference["bulk_edge_abs_eV"]),
                float(reference["binding_margin_eV"]),
            ],
            rtol=0.0,
            atol=spec.acceptance.dispersion_abs_eV,
        )
