from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExperimentStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    observed: float
    limit: float
    unit: str

    @property
    def passed(self) -> bool:
        return self.observed <= self.limit


@dataclass(frozen=True, slots=True)
class SpectrumPoint:
    kx_Ainv: float
    ky_Ainv: float
    lower_eV: float
    upper_eV: float
    analytic_lower_eV: float
    analytic_upper_eV: float


@dataclass(frozen=True, slots=True)
class SpinPoint:
    angle_rad: float
    band: str
    kx_Ainv: float
    ky_Ainv: float
    sx: float
    sy: float
    sz: float
    helicity: float


@dataclass(frozen=True, slots=True)
class Exp001Metrics:
    max_hermiticity_residual_eV: float
    max_analytic_spectrum_error_eV: float
    dirac_point_abs_eV: float
    max_particle_hole_error_eV: float
    max_spin_norm_error: float
    max_spin_momentum_dot: float
    max_abs_spin_z: float
    max_helicity_error: float
    max_time_reversal_residual_eV: float


@dataclass(frozen=True, slots=True)
class Exp001Result:
    experiment_id: str
    checks: tuple[CheckResult, ...]
    metrics: Exp001Metrics
    spectrum: tuple[SpectrumPoint, ...]
    spin_ring: tuple[SpinPoint, ...]

    @property
    def status(self) -> ExperimentStatus:
        return (
            ExperimentStatus.PASS
            if all(check.passed for check in self.checks)
            else ExperimentStatus.FAIL
        )
