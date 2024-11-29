"""Postprocess snapshot: remove source of filed (optional), shift snapshot data to center of mass and then change units (kpc -> pc)."""

import os
from pathlib import Path
from typing import Optional
from typing import Union

import agama
import numpy as np
from utils.snap import parse_nemo


def postprocess(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    remove_point_source: bool = False,
    source_mass: float = 4.37 * 10**10,
    output_file: Optional[str] = None,
):
    """
    Postprocess snapshot: remove source of filed (optional), shift snapshot data
    to center of mass and then change units (kpc -> pc).
    """
    # Sanity checks
    if not Path(filename).exists():
        raise RuntimeError(f"filename {filename} does not exist")
    if source_mass <= 0:
        raise RuntimeError(f"Source mass should be positive, got {source_mass} Msun")

    mpv = parse_nemo(
        filename, t=t, transpose=False
    )  # np.array with rows: mass, pos, vel; shape [N, 7]
    xv, masses = mpv[:, 1:], mpv[:, 0]

    # Remove source mass (optional)
    if remove_point_source:
        assert np.allclose(xv[-1], np.zeros((1, 6)), atol=1e-7), xv[-1]
        assert np.isclose(masses[-1], source_mass), masses[-1]

        xv, masses = xv[:-1], masses[:-1]

    # Calculate center of mass
    m_tot = np.sum(masses)
    xv_cm = np.sum(xv * masses.reshape((-1, 1)), axis=0) / m_tot

    # Move to center of mass
    xv = xv - xv_cm

    # Define scaling coefficients
    r_scale = 1e3  # kpc -> pc

    # Scale snapshot
    xv[:, :3] *= r_scale
    snap = (xv, masses)

    if output_file is not None:
        agama.writeSnapshot(output_file, particles=snap, format="nemo")

    return snap, xv_cm
