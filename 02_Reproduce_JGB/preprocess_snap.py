"""Preprocess snapshot: change units (pc -> kpc) and shift snapshot data, optional: add point source of field."""

import argparse
from pathlib import Path

import agama
import numpy as np
from utils.general import compute_gyrfalcon_parameters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Preprocess snapshot: change units (pc -> kpc) and shift snapshot data. "
        "Optional: add point source of field."
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Snapshot file in nemo format",
    )
    parser.add_argument(
        "--r-shift",
        type=float,
        nargs=3,
        default=[0, 0, 0],
        help="Shift in distances (in kiloparsecs)",
    )
    parser.add_argument(
        "--v-shift",
        type=float,
        nargs=3,
        default=[0, 0, 0],
        help="Shift in velocities (in km/s)",
    )
    parser.add_argument(
        "--plummer-r",
        "--r",
        type=float,
        default=10,
        help="Plummer sphere radius (in parsecs). Default: 10",
    )
    parser.add_argument(
        "--add-point-source",
        action="store_true",
        help="Whether to add steady point source of gravity "
        "at the center of coordinates (use '--source-mass' to set its mass).",
    )
    parser.add_argument(
        "--source-mass",
        type=float,
        default=4.37 * 10**10,
        help="Mass of point source of gravitational field (is solar masses). Default: 4.37x10^10",
    )
    args = parser.parse_args()

    # Sanity checks
    if args.plummer_r <= 0:
        raise RuntimeError(
            f"Plummer radius should be positive, got r={args.plummer_r} pc"
        )
    if args.source_mass <= 0:
        raise RuntimeError(
            f"Source mass should be positive, got {args.source_mass} Msun"
        )

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")

    # Compute gravitational constant in our units
    agama.setUnits(length=1, mass=1, velocity=1)  # 1 kpc, 1 Msun, 1 km/s
    Grav = agama.G

    # Define scaling coefficients
    r_scale = 1e-3  # pc -> kpc

    xv, masses = agama.readSnapshot(args.nemo_file)  # Shapes: [N, 6] and [N,]

    # Scale snapshot
    xv[:, :3] *= r_scale

    # Shift snapshot
    xv += np.array([*args.r_shift, *args.v_shift], dtype=np.float32)

    # Get the number of particles
    (N,) = masses.shape

    # Compute `eps`, `kmax` and dynamical time for gyrFalcON evolution in N-body units
    r_nbody = args.plummer_r * r_scale  # in kpcs
    m_nbody = np.sum(masses)
    phi0 = -m_nbody * Grav / r_nbody  # Plummer potential at zero

    eps, kmax, t_dyn = compute_gyrfalcon_parameters(N=N, r0=r_nbody, phi0=phi0)

    # Add point source of field (optional)
    if args.add_point_source:
        xv = np.concatenate((xv, np.zeros((1, 6))))
        masses = np.concatenate((masses, np.array([args.source_mass])))

    snap = (xv, masses)
    in_snap_file = args.nemo_file.replace(".nemo", "_preprocessed.nemo")
    out_snap_file = filename.parent / "out.nemo"

    agama.writeSnapshot(in_snap_file, snap, "nemo")

    print("*" * 10, "Transformation finished!", "*" * 10)
    print("Run this to start cluster evolution in N-body units for 1 dynamical time:")
    print(
        f"\tgyrfalcON {in_snap_file} {out_snap_file} logstep=3000 "
        f"eps={eps} kmax={kmax} tstop={t_dyn} step={t_dyn / 10} Grav={Grav}"
    )
