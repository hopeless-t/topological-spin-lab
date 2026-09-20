from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigh

from ..analytic.domain_wall import (
    bound_state_energy_eV,
    bound_state_envelope,
    bound_state_spinor,
    bulk_edge_abs_eV,
    localization_length_A,
)
from ..models.domain_wall import orientation_sign
from ..results import ExperimentStatus
from ..spec_val001 import Val001Spec
from .regulators import (
    build_stacey_system,
    build_wilson_system,
    physicalize_stacey_state,
)

_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_IDENTITY_2 = np.eye(2, dtype=np.complex128)


@dataclass(frozen=True, slots=True)
class ValidationGate:
    name: str
    passed: bool
    observed: str
    requirement: str


@dataclass(frozen=True, slots=True)
class Val001Observation:
    method: str
    grid_points: int
    dx_over_xi: float
    ky_Ainv: float
    orientation: str
    wilson_r: float | None
    target_energy_eV: float
    analytic_energy_eV: float
    energy_error_eV: float
    target_overlap: float
    profile_l1_error: float
    target_wall_weight: float
    target_edge_weight: float
    target_spin_x: float
    spin_x_error: float
    in_gap_count: int
    wall_localized_count: int
    boundary_artifact_count: int
    other_in_gap_count: int
    ghost_wall_modes: int
    matrix_hermiticity_residual_eV: float
    p_hermiticity_residual: float | None
    p_min_eigenvalue: float | None
    p_condition_number: float | None
    solver_seconds: float


@dataclass(frozen=True, slots=True)
class Val001MethodSummary:
    method: str
    wilson_r: float | None
    hard_pass: bool
    failed_gates: tuple[str, ...]
    max_energy_error_eV: float
    min_target_overlap: float
    max_profile_l1_error: float
    finest_profile_l1_error: float
    min_target_wall_weight: float
    max_target_edge_weight: float
    max_spin_x_error: float
    max_ghost_wall_modes: int
    max_boundary_artifacts: int
    max_other_in_gap_modes: int
    max_matrix_hermiticity_residual_eV: float
    max_p_hermiticity_residual: float | None
    min_p_eigenvalue: float | None
    max_p_condition_number: float | None
    monotone_profile_convergence: bool
    profile_l1_by_grid: tuple[tuple[int, float], ...]
    total_solver_seconds: float


@dataclass(frozen=True, slots=True)
class Val001Result:
    validation_id: str
    gates: tuple[ValidationGate, ...]
    observations: tuple[Val001Observation, ...]
    method_summaries: tuple[Val001MethodSummary, ...]
    spectral_validator: str
    best_wilson_r: float
    transport_candidate: str
    transport_authorized: bool
    total_solver_seconds: float

    @property
    def status(self) -> ExperimentStatus:
        return (
            ExperimentStatus.PASS
            if all(gate.passed for gate in self.gates)
            else ExperimentStatus.FAIL
        )


@dataclass(frozen=True, slots=True)
class _StateMetrics:
    overlap: float
    profile_l1_error: float
    wall_weight: float
    edge_weight: float
    spin_x: float


def _normalize(state: NDArray[np.complex128]) -> NDArray[np.complex128]:
    vector = np.asarray(state, dtype=np.complex128).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if norm == 0.0 or not math.isfinite(norm):
        raise ValueError("State has invalid norm.")
    return vector / norm


def _analytic_target(
    x_A: NDArray[np.float64],
    spec: Val001Spec,
    orientation: str,
) -> NDArray[np.complex128]:
    envelope = bound_state_envelope(
        x_A,
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
        spec.reference.wall_width_A,
    )
    spinor = bound_state_spinor(orientation)
    return _normalize((envelope[:, None] * spinor[None, :]).reshape(-1))


def _spin_x(state: NDArray[np.complex128]) -> float:
    vector = _normalize(state)
    spinor = vector.reshape(-1, 2)
    local = np.einsum(
        "ni,ij,nj->n",
        spinor.conj(),
        _SIGMA_X,
        spinor,
    )
    return float(np.real(np.sum(local)))


def _state_metrics(
    state: NDArray[np.complex128],
    x_A: NDArray[np.float64],
    target: NDArray[np.complex128],
    spec: Val001Spec,
) -> _StateMetrics:
    vector = _normalize(state)
    spinor = vector.reshape(len(x_A), 2)
    density = np.sum(np.abs(spinor) ** 2, axis=1)
    density = density / float(np.sum(density))

    target_spinor = target.reshape(len(x_A), 2)
    target_density = np.sum(np.abs(target_spinor) ** 2, axis=1)
    target_density = target_density / float(np.sum(target_density))

    xi_A = localization_length_A(
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    wall_mask = np.abs(x_A) <= spec.classification.wall_half_width_xi * xi_A
    edge_mask = np.abs(x_A) >= spec.classification.edge_start_xi * xi_A

    return _StateMetrics(
        overlap=float(abs(np.vdot(target, vector)) ** 2),
        profile_l1_error=float(np.sum(np.abs(density - target_density))),
        wall_weight=float(np.sum(density[wall_mask])),
        edge_weight=float(np.sum(density[edge_mask])),
        spin_x=_spin_x(vector),
    )


def _localized_zero_subspace(
    eigenvalues_eV: NDArray[np.float64],
    physical_states: NDArray[np.complex128],
    in_gap_indices: NDArray[np.int64],
    x_A: NDArray[np.float64],
    spec: Val001Spec,
) -> tuple[list[tuple[float, NDArray[np.complex128]]], set[int]]:
    zero_indices = [
        int(index)
        for index in in_gap_indices
        if abs(float(eigenvalues_eV[index])) <= spec.classification.zero_subspace_eV
    ]
    if not zero_indices:
        raise ValueError("No near-zero subspace was available at ky=0.")

    zero_states = physical_states[:, zero_indices]
    xi_A = localization_length_A(
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    wall_mask = np.abs(x_A) <= spec.classification.wall_half_width_xi * xi_A
    wall_projector = np.kron(
        np.diag(wall_mask.astype(np.float64)),
        _IDENTITY_2,
    )

    localization_matrix = (
        zero_states.conj().T @ wall_projector @ zero_states
    )
    localization_matrix = 0.5 * (
        localization_matrix + localization_matrix.conj().T
    )
    _, rotation = eigh(localization_matrix)

    diagonal_energies = np.diag(eigenvalues_eV[zero_indices])
    localized: list[tuple[float, NDArray[np.complex128]]] = []
    for column in range(rotation.shape[1]):
        coefficients = rotation[:, column]
        state = _normalize(zero_states @ coefficients)
        energy = float(
            np.real(
                coefficients.conj().T
                @ diagonal_energies
                @ coefficients
            )
        )
        localized.append((energy, state))

    return localized, set(zero_indices)


def _classify_in_gap_states(
    states: list[NDArray[np.complex128]],
    x_A: NDArray[np.float64],
    target: NDArray[np.complex128],
    spec: Val001Spec,
) -> tuple[int, int, int]:
    wall = 0
    edge = 0
    other = 0

    for state in states:
        metrics = _state_metrics(state, x_A, target, spec)
        if metrics.wall_weight >= spec.classification.wall_localization_min:
            wall += 1
        elif metrics.edge_weight >= spec.classification.edge_localization_min:
            edge += 1
        else:
            other += 1

    return wall, edge, other


def _evaluate_spectrum(
    *,
    eigenvalues_eV: NDArray[np.float64],
    physical_states: NDArray[np.complex128],
    x_A: NDArray[np.float64],
    ky_Ainv: float,
    orientation: str,
    spec: Val001Spec,
) -> tuple[float, _StateMetrics, int, int, int, int]:
    bulk_edge = bulk_edge_abs_eV(
        ky_Ainv,
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    in_gap_indices = np.flatnonzero(
        np.abs(eigenvalues_eV)
        < bulk_edge - spec.classification.in_gap_margin_eV
    ).astype(np.int64)
    if len(in_gap_indices) == 0:
        raise ValueError("No in-gap state was found.")

    target = _analytic_target(x_A, spec, orientation)

    classification_states: list[NDArray[np.complex128]] = []
    target_candidates: list[tuple[float, NDArray[np.complex128]]] = []

    if math.isclose(ky_Ainv, 0.0, rel_tol=0.0, abs_tol=1e-15):
        localized, consumed = _localized_zero_subspace(
            eigenvalues_eV,
            physical_states,
            in_gap_indices,
            x_A,
            spec,
        )
        classification_states.extend(state for _, state in localized)
        target_candidates.extend(localized)

        for index in in_gap_indices:
            if int(index) not in consumed:
                state = _normalize(physical_states[:, int(index)])
                classification_states.append(state)
                target_candidates.append(
                    (float(eigenvalues_eV[int(index)]), state)
                )
    else:
        for index in in_gap_indices:
            state = _normalize(physical_states[:, int(index)])
            classification_states.append(state)
            target_candidates.append(
                (float(eigenvalues_eV[int(index)]), state)
            )

    if not target_candidates:
        raise ValueError("No target candidates were available.")

    target_energy, target_state = max(
        target_candidates,
        key=lambda item: _state_metrics(item[1], x_A, target, spec).overlap,
    )
    metrics = _state_metrics(target_state, x_A, target, spec)

    wall_count, boundary_count, other_count = _classify_in_gap_states(
        classification_states,
        x_A,
        target,
        spec,
    )
    ghost_wall_modes = max(0, wall_count - 1)

    return (
        target_energy,
        metrics,
        len(in_gap_indices),
        wall_count,
        boundary_count,
        other_count,
        ghost_wall_modes,
    )


def _solve_wilson(
    spec: Val001Spec,
    *,
    grid_points: int,
    ky_Ainv: float,
    orientation: str,
    wilson_r: float,
) -> Val001Observation:
    xi_A = localization_length_A(
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    half_window_A = spec.reference.half_window_xi * xi_A
    system = build_wilson_system(
        grid_points=grid_points,
        half_window_A=half_window_A,
        ky_Ainv=ky_Ainv,
        alpha_eV_A=spec.reference.alpha_eV_A,
        mass_magnitude_eV=spec.reference.mass_magnitude_eV,
        wall_width_A=spec.reference.wall_width_A,
        orientation=orientation,
        wilson_r=wilson_r,
    )

    bulk_edge = bulk_edge_abs_eV(
        ky_Ainv,
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    window = 1.02 * bulk_edge

    start = time.perf_counter()
    eigenvalues, eigenvectors = eigh(
        system.hamiltonian_eV,
        subset_by_value=(-window, window),
        check_finite=True,
    )
    solver_seconds = time.perf_counter() - start

    (
        target_energy,
        state_metrics,
        in_gap_count,
        wall_count,
        boundary_count,
        other_count,
        ghost_count,
    ) = _evaluate_spectrum(
        eigenvalues_eV=eigenvalues,
        physical_states=eigenvectors,
        x_A=system.x_A,
        ky_Ainv=ky_Ainv,
        orientation=orientation,
        spec=spec,
    )

    analytic_energy = bound_state_energy_eV(
        ky_Ainv,
        spec.reference.alpha_eV_A,
        orientation,
    )
    expected_spin_x = -orientation_sign(orientation)

    spacing_A = float(system.x_A[1] - system.x_A[0])
    return Val001Observation(
        method="wilson",
        grid_points=grid_points,
        dx_over_xi=spacing_A / xi_A,
        ky_Ainv=ky_Ainv,
        orientation=orientation,
        wilson_r=wilson_r,
        target_energy_eV=target_energy,
        analytic_energy_eV=analytic_energy,
        energy_error_eV=abs(target_energy - analytic_energy),
        target_overlap=state_metrics.overlap,
        profile_l1_error=state_metrics.profile_l1_error,
        target_wall_weight=state_metrics.wall_weight,
        target_edge_weight=state_metrics.edge_weight,
        target_spin_x=state_metrics.spin_x,
        spin_x_error=abs(state_metrics.spin_x - expected_spin_x),
        in_gap_count=in_gap_count,
        wall_localized_count=wall_count,
        boundary_artifact_count=boundary_count,
        other_in_gap_count=other_count,
        ghost_wall_modes=ghost_count,
        matrix_hermiticity_residual_eV=float(
            np.max(
                np.abs(
                    system.hamiltonian_eV
                    - system.hamiltonian_eV.conj().T
                )
            )
        ),
        p_hermiticity_residual=None,
        p_min_eigenvalue=None,
        p_condition_number=None,
        solver_seconds=solver_seconds,
    )


def _solve_stacey(
    spec: Val001Spec,
    *,
    grid_points: int,
    ky_Ainv: float,
    orientation: str,
) -> Val001Observation:
    xi_A = localization_length_A(
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    half_window_A = spec.reference.half_window_xi * xi_A
    system = build_stacey_system(
        grid_points=grid_points,
        half_window_A=half_window_A,
        ky_Ainv=ky_Ainv,
        alpha_eV_A=spec.reference.alpha_eV_A,
        mass_magnitude_eV=spec.reference.mass_magnitude_eV,
        wall_width_A=spec.reference.wall_width_A,
        orientation=orientation,
    )

    bulk_edge = bulk_edge_abs_eV(
        ky_Ainv,
        spec.reference.alpha_eV_A,
        spec.reference.mass_magnitude_eV,
    )
    window = 1.02 * bulk_edge

    start = time.perf_counter()
    eigenvalues, generalized_states = eigh(
        system.hamiltonian_eV,
        system.metric,
        subset_by_value=(-window, window),
        check_finite=True,
    )
    solver_seconds = time.perf_counter() - start

    physical_states = np.column_stack(
        [
            _normalize(
                physicalize_stacey_state(
                    generalized_states[:, column],
                    system.phi,
                ).reshape(-1)
            )
            for column in range(generalized_states.shape[1])
        ]
    )

    (
        target_energy,
        state_metrics,
        in_gap_count,
        wall_count,
        boundary_count,
        other_count,
        ghost_count,
    ) = _evaluate_spectrum(
        eigenvalues_eV=eigenvalues,
        physical_states=physical_states,
        x_A=system.interface_x_A,
        ky_Ainv=ky_Ainv,
        orientation=orientation,
        spec=spec,
    )

    p_eigenvalues = np.linalg.eigvalsh(system.metric)
    analytic_energy = bound_state_energy_eV(
        ky_Ainv,
        spec.reference.alpha_eV_A,
        orientation,
    )
    expected_spin_x = -orientation_sign(orientation)

    spacing_A = float(system.x_A[1] - system.x_A[0])
    return Val001Observation(
        method="stacey",
        grid_points=grid_points,
        dx_over_xi=spacing_A / xi_A,
        ky_Ainv=ky_Ainv,
        orientation=orientation,
        wilson_r=None,
        target_energy_eV=target_energy,
        analytic_energy_eV=analytic_energy,
        energy_error_eV=abs(target_energy - analytic_energy),
        target_overlap=state_metrics.overlap,
        profile_l1_error=state_metrics.profile_l1_error,
        target_wall_weight=state_metrics.wall_weight,
        target_edge_weight=state_metrics.edge_weight,
        target_spin_x=state_metrics.spin_x,
        spin_x_error=abs(state_metrics.spin_x - expected_spin_x),
        in_gap_count=in_gap_count,
        wall_localized_count=wall_count,
        boundary_artifact_count=boundary_count,
        other_in_gap_count=other_count,
        ghost_wall_modes=ghost_count,
        matrix_hermiticity_residual_eV=float(
            np.max(
                np.abs(
                    system.hamiltonian_eV
                    - system.hamiltonian_eV.conj().T
                )
            )
        ),
        p_hermiticity_residual=float(
            np.max(np.abs(system.metric - system.metric.conj().T))
        ),
        p_min_eigenvalue=float(np.min(p_eigenvalues)),
        p_condition_number=float(
            np.max(p_eigenvalues) / np.min(p_eigenvalues)
        ),
        solver_seconds=solver_seconds,
    )


def _method_key(method: str, wilson_r: float | None) -> str:
    if method == "stacey":
        return "stacey"
    if wilson_r is None:
        raise ValueError("Wilson method requires wilson_r.")
    return f"wilson:r={wilson_r:g}"


def _summarize_method(
    observations: list[Val001Observation],
    spec: Val001Spec,
) -> Val001MethodSummary:
    if not observations:
        raise ValueError("Cannot summarize an empty method result.")

    method = observations[0].method
    wilson_r = observations[0].wilson_r
    if any(
        item.method != method or item.wilson_r != wilson_r
        for item in observations
    ):
        raise ValueError("Method summary received mixed variants.")

    grid_profile: list[tuple[int, float]] = []
    for grid_points in spec.sampling.grid_points:
        values = [
            item.profile_l1_error
            for item in observations
            if item.grid_points == grid_points
        ]
        grid_profile.append((grid_points, max(values)))

    monotone = all(
        right <= left + 1e-12
        for (_, left), (_, right) in zip(
            grid_profile,
            grid_profile[1:],
            strict=False,
        )
    )

    max_energy = max(item.energy_error_eV for item in observations)
    min_overlap = min(item.target_overlap for item in observations)
    max_profile = max(item.profile_l1_error for item in observations)
    finest_grid = max(spec.sampling.grid_points)
    finest_profile = max(
        item.profile_l1_error
        for item in observations
        if item.grid_points == finest_grid
    )
    min_wall = min(item.target_wall_weight for item in observations)
    max_edge = max(item.target_edge_weight for item in observations)
    max_spin = max(item.spin_x_error for item in observations)
    max_ghost = max(item.ghost_wall_modes for item in observations)
    max_boundary = max(item.boundary_artifact_count for item in observations)
    max_other = max(item.other_in_gap_count for item in observations)
    max_hermiticity = max(
        item.matrix_hermiticity_residual_eV for item in observations
    )

    p_hermiticity_values = [
        item.p_hermiticity_residual
        for item in observations
        if item.p_hermiticity_residual is not None
    ]
    p_min_values = [
        item.p_min_eigenvalue
        for item in observations
        if item.p_min_eigenvalue is not None
    ]
    p_condition_values = [
        item.p_condition_number
        for item in observations
        if item.p_condition_number is not None
    ]

    max_p_hermiticity = (
        max(p_hermiticity_values) if p_hermiticity_values else None
    )
    min_p_eigenvalue = min(p_min_values) if p_min_values else None
    max_p_condition = max(p_condition_values) if p_condition_values else None

    acceptance = spec.acceptance
    failed: list[str] = []

    if max_energy > acceptance.target_energy_abs_eV:
        failed.append("target_energy")
    if min_overlap < acceptance.target_overlap_min:
        failed.append("target_overlap")
    if min_wall < acceptance.target_wall_weight_min:
        failed.append("target_wall_weight")
    if max_edge > acceptance.target_edge_weight_max:
        failed.append("target_edge_weight")
    if max_spin > acceptance.spin_x_abs:
        failed.append("spin_x")
    if finest_profile > acceptance.finest_profile_l1_max:
        failed.append("finest_profile_l1")
    if max_ghost > acceptance.max_ghost_wall_modes:
        failed.append("ghost_wall_modes")
    if max_boundary > acceptance.max_boundary_artifacts:
        failed.append("boundary_artifacts")
    if max_other > acceptance.max_other_in_gap_modes:
        failed.append("other_in_gap_modes")
    if max_hermiticity > acceptance.matrix_hermiticity_abs_eV:
        failed.append("matrix_hermiticity")
    if (
        acceptance.require_monotone_profile_convergence
        and not monotone
    ):
        failed.append("profile_convergence")

    if method == "stacey":
        if max_p_hermiticity is None or (
            max_p_hermiticity > acceptance.p_hermiticity_abs
        ):
            failed.append("p_hermiticity")
        if min_p_eigenvalue is None or (
            min_p_eigenvalue < acceptance.p_min_eigenvalue_min
        ):
            failed.append("p_positive_definite")

    return Val001MethodSummary(
        method=method,
        wilson_r=wilson_r,
        hard_pass=not failed,
        failed_gates=tuple(failed),
        max_energy_error_eV=max_energy,
        min_target_overlap=min_overlap,
        max_profile_l1_error=max_profile,
        finest_profile_l1_error=finest_profile,
        min_target_wall_weight=min_wall,
        max_target_edge_weight=max_edge,
        max_spin_x_error=max_spin,
        max_ghost_wall_modes=max_ghost,
        max_boundary_artifacts=max_boundary,
        max_other_in_gap_modes=max_other,
        max_matrix_hermiticity_residual_eV=max_hermiticity,
        max_p_hermiticity_residual=max_p_hermiticity,
        min_p_eigenvalue=min_p_eigenvalue,
        max_p_condition_number=max_p_condition,
        monotone_profile_convergence=monotone,
        profile_l1_by_grid=tuple(grid_profile),
        total_solver_seconds=sum(
            item.solver_seconds for item in observations
        ),
    )


def execute_val001(spec: Val001Spec) -> Val001Result:
    observations: list[Val001Observation] = []

    for grid_points in spec.sampling.grid_points:
        for orientation in spec.sampling.orientations:
            for ky_Ainv in spec.sampling.ky_Ainv:
                observations.append(
                    _solve_stacey(
                        spec,
                        grid_points=grid_points,
                        ky_Ainv=ky_Ainv,
                        orientation=orientation,
                    )
                )
                for wilson_r in spec.sampling.wilson_r:
                    observations.append(
                        _solve_wilson(
                            spec,
                            grid_points=grid_points,
                            ky_Ainv=ky_Ainv,
                            orientation=orientation,
                            wilson_r=wilson_r,
                        )
                    )

    grouped: dict[str, list[Val001Observation]] = {}
    for observation in observations:
        key = _method_key(observation.method, observation.wilson_r)
        grouped.setdefault(key, []).append(observation)

    summaries = tuple(
        _summarize_method(grouped[key], spec)
        for key in sorted(grouped)
    )
    passing = [summary for summary in summaries if summary.hard_pass]
    stacey = next(
        (summary for summary in summaries if summary.method == "stacey"),
        None,
    )
    passing_wilson = [
        summary
        for summary in passing
        if summary.method == "wilson"
    ]

    best_wilson = (
        min(
            passing_wilson,
            key=lambda item: (
                item.finest_profile_l1_error,
                -item.min_target_overlap,
                item.max_energy_error_eV,
            ),
        )
        if passing_wilson
        else None
    )
    spectral_validator_summary = (
        min(
            passing,
            key=lambda item: (
                item.finest_profile_l1_error,
                -item.min_target_overlap,
                item.max_energy_error_eV,
            ),
        )
        if passing
        else None
    )

    gates = (
        ValidationGate(
            name="stacey_valid",
            passed=bool(stacey is not None and stacey.hard_pass),
            observed=(
                "PASS" if stacey is not None and stacey.hard_pass else "FAIL"
            ),
            requirement="Stacey/tangent generalized eigensolver passes hard gates.",
        ),
        ValidationGate(
            name="wilson_candidate_available",
            passed=best_wilson is not None,
            observed=(
                _method_key(best_wilson.method, best_wilson.wilson_r)
                if best_wilson is not None
                else "none"
            ),
            requirement="At least one Wilson-r variant passes hard gates.",
        ),
        ValidationGate(
            name="spectral_validator_available",
            passed=spectral_validator_summary is not None,
            observed=(
                _method_key(
                    spectral_validator_summary.method,
                    spectral_validator_summary.wilson_r,
                )
                if spectral_validator_summary is not None
                else "none"
            ),
            requirement="At least one regulator can serve as continuum spectral validator.",
        ),
        ValidationGate(
            name="independent_roles_available",
            passed=bool(
                spectral_validator_summary is not None
                and best_wilson is not None
                and spectral_validator_summary.method != best_wilson.method
            ),
            observed=(
                (
                    f"validator={_method_key(spectral_validator_summary.method, spectral_validator_summary.wilson_r)}, "
                    f"transport_candidate={_method_key(best_wilson.method, best_wilson.wilson_r)}"
                )
                if spectral_validator_summary is not None
                and best_wilson is not None
                else "incomplete"
            ),
            requirement=(
                "Validation oracle and conventional-lattice transport candidate "
                "come from different regulator families."
            ),
        ),
    )

    spectral_validator = (
        _method_key(
            spectral_validator_summary.method,
            spectral_validator_summary.wilson_r,
        )
        if spectral_validator_summary is not None
        else "none"
    )
    best_wilson_r = (
        float(best_wilson.wilson_r)
        if best_wilson is not None and best_wilson.wilson_r is not None
        else math.nan
    )
    transport_candidate = (
        _method_key(best_wilson.method, best_wilson.wilson_r)
        if best_wilson is not None
        else "none"
    )

    return Val001Result(
        validation_id=spec.validation_id,
        gates=gates,
        observations=tuple(observations),
        method_summaries=summaries,
        spectral_validator=spectral_validator,
        best_wilson_r=best_wilson_r,
        transport_candidate=transport_candidate,
        transport_authorized=False,
        total_solver_seconds=sum(
            item.solver_seconds for item in observations
        ),
    )
