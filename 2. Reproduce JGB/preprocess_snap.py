"""Preprocess snapshot: change units (pc -> kpc) and shift snapshot data, optional: add point source of field."""

import argparse
from pathlib import Path

import agama
import numpy as np
from utils.general import compute_gyrfalcon_parameters
from utils.transform_snap import create_center_mass_snapshot
from utils.transform_snap import scale_snapshot
from utils.transform_snap import shift_snapshot
from utils.transform_snap import stack_snapshot
from utils.transform_snap import test_center_mass_snapshot
from utils.transform_snap import test_scale
from utils.transform_snap import test_shift
from utils.transform_snap import test_stack

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
    parser.add_argument(
        "--test",
        action="store_true",
        help="Whether to test snapshot conversion for correctness",
    )
    args = parser.parse_args()

    # Sanity checks
    if args.plummer_r <= 0:
        raise RuntimeError(
            f"Plummer radius should be positive, got r={args.plummer_r} pc"
        )

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")

    # Compute gravitational constant in our units
    agama.setUnits(length=1, mass=1, velocity=1)  # 1 kpc, 1 Msun, 1 km/s
    Grav = agama.G

    # Define scaling coefficients
    r_scale = 1e-3  # pc -> kpc
    v_scale = 1.0
    m_scale = 1.0

    # Transform snapshot
    snapshot_scaled = args.nemo_file.replace(".nemo", "_scaled.nemo")
    snapshot_shifted = snapshot_scaled.replace(".nemo", "_shifted.nemo")

    scale_snapshot(
        filename=args.nemo_file,
        outfile=snapshot_scaled,
        rscale=r_scale,
        vscale=v_scale,
        mscale=m_scale,
    )
    if args.test:
        test_scale(
            filename=args.nemo_file,
            outfile=snapshot_scaled,
            rscale=r_scale,
            vscale=v_scale,
            mscale=m_scale,
        )

    shift_snapshot(
        filename=snapshot_scaled,
        outfile=snapshot_shifted,
        rshift=args.r_shift,
        vshift=args.v_shift,
    )
    if args.test:
        test_shift(
            filename=snapshot_scaled,
            outfile=snapshot_shifted,
            rshift=args.r_shift,
            vshift=args.v_shift,
        )

    # Read nemo file to get the number of particles
    xv, masses = agama.readSnapshot(args.nemo_file)
    (N,) = masses.shape

    # Compute `eps`, `kmax` and dynamical time for gyrFalcON evolution in N-body units
    r_nbody = args.plummer_r * r_scale  # in kpcs
    m_nbody = np.sum(masses)
    phi0 = -m_nbody * Grav / r_nbody  # Plummer potential at zero

    eps, kmax, t_dyn = compute_gyrfalcon_parameters(N=N, r0=r_nbody, phi0=phi0)

    # Add point source of field (optional)
    if args.add_point_source:
        snapshot_central_mass = args.nemo_file.replace(".nemo", "_potential.nemo")

        create_center_mass_snapshot(
            filename=snapshot_central_mass,
            mass=args.source_mass,
        )
        if args.test:
            test_center_mass_snapshot(
                filename=snapshot_central_mass,
                mass=args.source_mass,
            )

        stack_snapshot(
            filename1=snapshot_shifted,
            filename2=snapshot_central_mass,
            outfile=snapshot_with_potential,
        )
        if args.test:
            test_stack(
                filename1=snapshot_shifted,
                filename2=snapshot_central_mass,
                outfile=snapshot_with_potential,
            )

    input_snap_file = (
        snapshot_with_potential if args.add_point_source else snapshot_shifted
    )
    out_snap_file = filename.parent / "out_pot.nemo"

    print("*" * 10, "Transformation finished!", "*" * 10)
    print("Run this to start cluster evolution in N-body units for 1 dynamical time:")
    print(
        f"\tgyrfalcON {input_snap_file} {out_snap_file} logstep=300 "
        f"eps={eps} kmax={kmax} tstop={t_dyn} step={t_dyn / 100} Grav={Grav}"
    )
