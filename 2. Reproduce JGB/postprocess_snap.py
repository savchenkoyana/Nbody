"""Postprocess snapshot: remove source of filed (optional), shift snapshot data to center of mass and then change units (kpc -> pc)."""

import argparse
from pathlib import Path

import agama
import numpy as np
from utils.general import set_units

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Postprocess snapshot: remove source of filed (optional), shift snapshot data "
        "to center of mass and then change units (kpc -> pc)."
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Snapshot file in nemo format",
    )
    parser.add_argument(
        "--remove-point-source",
        action="store_true",
        help="Whether to remove a steady point source of gravity at the center of coordinates.",
    )
    parser.add_argument(
        "--source-mass",
        type=float,
        default=4.37 * 10**10,
        help="Mass of point source of gravitational field (is solar masses). Default: 4.37x10^10",
    )
    args = parser.parse_args()

    # Sanity checks
    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")
    if args.source_mass <= 0:
        raise RuntimeError(
            f"Source mass should be positive, got {args.source_mass} Msun"
        )

    set_units()

    xv, masses = agama.readSnapshot(args.nemo_file)  # Shapes: [N, 6] and [N,]

    # Remove source mass (optional)
    if args.remove_point_source:
        assert np.allclose(xv[-1], np.zeros((1, 6)))
        assert np.isclose(masses[-1], args.source_mass)

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

    # Save
    snap = (xv, masses)
    snap_file = args.nemo_file.replace(".nemo", "_postprocessed.nemo")
    agama.writeSnapshot(snap_file, snap, "nemo")
