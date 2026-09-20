from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .results import Exp001Result


def write_figures(result: Exp001Result, output_dir: Path) -> tuple[Path, Path]:
    """Render human-inspection figures from already-computed observations."""
    output_dir.mkdir(parents=True, exist_ok=True)

    spectrum_path = output_dir / "dirac_cone.png"
    spin_path = output_dir / "spin_texture.png"

    kx = np.array([point.kx_Ainv for point in result.spectrum])
    lower = np.array([point.lower_eV for point in result.spectrum])
    upper = np.array([point.upper_eV for point in result.spectrum])

    fig, ax = plt.subplots()
    ax.plot(kx, lower)
    ax.plot(kx, upper)
    ax.set_xlabel(r"$k_x$ ($\AA^{-1}$)")
    ax.set_ylabel("Energy (eV)")
    ax.set_title("EXP-001: massless surface Dirac spectrum")
    fig.tight_layout()
    fig.savefig(spectrum_path, dpi=160)
    plt.close(fig)

    upper_points = [point for point in result.spin_ring if point.band == "upper"]
    kx_ring = np.array([point.kx_Ainv for point in upper_points])
    ky_ring = np.array([point.ky_Ainv for point in upper_points])
    sx = np.array([point.sx for point in upper_points])
    sy = np.array([point.sy for point in upper_points])

    fig, ax = plt.subplots()
    ax.quiver(kx_ring, ky_ring, sx, sy)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel(r"$k_x$ ($\AA^{-1}$)")
    ax.set_ylabel(r"$k_y$ ($\AA^{-1}$)")
    ax.set_title("EXP-001: upper-band spin texture")
    fig.tight_layout()
    fig.savefig(spin_path, dpi=160)
    plt.close(fig)

    return spectrum_path, spin_path
