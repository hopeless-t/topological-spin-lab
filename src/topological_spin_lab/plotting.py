from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .results import Exp001Result, Exp002Result, Exp003Result


def _write_spectrum_figure(
    result: Exp001Result | Exp002Result,
    output_dir: Path,
    title: str,
    filename: str,
) -> Path:
    kx = np.array([point.kx_Ainv for point in result.spectrum])
    lower = np.array([point.lower_eV for point in result.spectrum])
    upper = np.array([point.upper_eV for point in result.spectrum])

    path = output_dir / filename
    fig, ax = plt.subplots()
    ax.plot(kx, lower)
    ax.plot(kx, upper)
    ax.set_xlabel(r"$k_x$ ($\AA^{-1}$)")
    ax.set_ylabel("Energy (eV)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def _write_spin_figure(
    result: Exp001Result | Exp002Result,
    output_dir: Path,
    title: str,
    filename: str,
) -> Path:
    upper_points = [point for point in result.spin_ring if point.band == "upper"]
    kx_ring = np.array([point.kx_Ainv for point in upper_points])
    ky_ring = np.array([point.ky_Ainv for point in upper_points])
    sx = np.array([point.sx for point in upper_points])
    sy = np.array([point.sy for point in upper_points])

    path = output_dir / filename
    fig, ax = plt.subplots()
    ax.quiver(kx_ring, ky_ring, sx, sy)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$k_x$ ($\AA^{-1}$)")
    ax.set_ylabel(r"$k_y$ ($\AA^{-1}$)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path


def write_figures(result: Exp001Result, output_dir: Path) -> tuple[Path, Path]:
    """Render EXP-001 human-inspection figures from computed observations."""
    output_dir.mkdir(parents=True, exist_ok=True)
    spectrum_path = _write_spectrum_figure(
        result,
        output_dir,
        "EXP-001: massless surface Dirac spectrum",
        "dirac_cone.png",
    )
    spin_path = _write_spin_figure(
        result,
        output_dir,
        "EXP-001: upper-band spin texture",
        "spin_texture.png",
    )
    return spectrum_path, spin_path


def write_exp002_figures(
    result: Exp002Result,
    output_dir: Path,
) -> tuple[Path, Path, Path]:
    """Render EXP-002 human-inspection figures from computed observations."""
    output_dir.mkdir(parents=True, exist_ok=True)
    spectrum_path = _write_spectrum_figure(
        result,
        output_dir,
        "EXP-002: magnetically gapped surface Dirac spectrum",
        "magnetic_dirac_spectrum.png",
    )
    spin_path = _write_spin_figure(
        result,
        output_dir,
        "EXP-002: upper-band in-plane spin projection",
        "spin_texture.png",
    )

    upper_points = [point for point in result.spin_ring if point.band == "upper"]
    angles = np.array([point.angle_rad for point in upper_points])
    sz = np.array([point.sz for point in upper_points])

    spin_z_path = output_dir / "spin_z.png"
    fig, ax = plt.subplots()
    ax.plot(angles, sz)
    ax.set_xlabel("Angle (rad)")
    ax.set_ylabel(r"$\langle \sigma_z \rangle$")
    ax.set_title("EXP-002: upper-band out-of-plane spin")
    fig.tight_layout()
    fig.savefig(spin_z_path, dpi=160)
    plt.close(fig)

    return spectrum_path, spin_path, spin_z_path



def write_exp003_figures(
    result: Exp003Result,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Render EXP-003 human-inspection figures from computed observations."""
    output_dir.mkdir(parents=True, exist_ok=True)

    profile_path = output_dir / "domain_wall_profile.png"
    x = np.array([point.x_A for point in result.profile])
    mass = np.array([point.mass_eV for point in result.profile])
    density = np.array([point.probability_density_Ainv for point in result.profile])

    fig, ax = plt.subplots()
    ax.plot(x, mass, label="mass (eV)")
    ax.plot(x, density, label="probability density (A^-1)")
    ax.set_xlabel("x (A)")
    ax.set_title("EXP-003: domain wall and localized bound mode")
    ax.legend()
    fig.tight_layout()
    fig.savefig(profile_path, dpi=160)
    plt.close(fig)

    dispersion_path = output_dir / "domain_wall_dispersion.png"
    ky = np.array([point.ky_Ainv for point in result.dispersion])
    energy = np.array([point.energy_eV for point in result.dispersion])
    bulk = np.array([point.bulk_edge_abs_eV for point in result.dispersion])

    fig, ax = plt.subplots()
    ax.plot(ky, energy, label="bound mode")
    ax.plot(ky, bulk, label="+ bulk edge")
    ax.plot(ky, -bulk, label="- bulk edge")
    ax.set_xlabel(r"$k_y$ ($\AA^{-1}$)")
    ax.set_ylabel("Energy (eV)")
    ax.set_title("EXP-003: chiral domain-wall dispersion")
    ax.legend()
    fig.tight_layout()
    fig.savefig(dispersion_path, dpi=160)
    plt.close(fig)

    return profile_path, dispersion_path
