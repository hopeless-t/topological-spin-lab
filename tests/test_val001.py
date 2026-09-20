from __future__ import annotations

from pathlib import Path

from topological_spin_lab.results import ExperimentStatus
from topological_spin_lab.spec_val001 import load_val001_spec
from topological_spin_lab.validation.val001 import execute_val001

ROOT = Path(__file__).resolve().parents[1]


def test_full_val001_crosscheck_passes_and_keeps_roles_separate() -> None:
    spec = load_val001_spec(ROOT / "specs" / "VAL-001.json")
    result = execute_val001(spec)

    assert result.status is ExperimentStatus.PASS
    assert len(result.observations) == 120
    assert len(result.method_summaries) == 4
    assert result.spectral_validator == "stacey"
    assert result.best_wilson_r == 0.5
    assert result.transport_candidate == "wilson:r=0.5"
    assert result.transport_authorized is False

    stacey = next(
        summary
        for summary in result.method_summaries
        if summary.method == "stacey"
    )
    best_wilson = next(
        summary
        for summary in result.method_summaries
        if summary.method == "wilson" and summary.wilson_r == 0.5
    )

    assert stacey.hard_pass
    assert best_wilson.hard_pass
    assert stacey.max_ghost_wall_modes == 0
    assert best_wilson.max_ghost_wall_modes == 0
    assert stacey.finest_profile_l1_error < best_wilson.finest_profile_l1_error
