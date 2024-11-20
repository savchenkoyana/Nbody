"""Transform snapshot: change units (pc -> kpc) and shift snapshot data."""

import argparse
import os
import subprocess
from pathlib import Path
from typing import Annotated
from typing import Union

import agama
import numpy as np
from create_ic import compute_gyrfalcon_parameters


def scale_snapshot(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rscale: float,
    vscale: float,
    mscale: float,
):
    if os.path.exists(outfile):
        print(f"{outfile} already exists! removing...")
        os.remove(outfile)

    command = f"snapscale in={filename} out={outfile} rscale={rscale} vscale={vscale} mscale={mscale} | tee snapscale_log 2>&1"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


def test_scale(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rscale: float,
    vscale: float,
    mscale: float,
):
    coords_before = agama.readSnapshot(filename)  # tuple of (xv[N, 6], m[N,])
    coords_after = agama.readSnapshot(outfile)

    assert np.allclose(coords_before[1], coords_after[1] / mscale, atol=5e-6)  # masses
    assert np.allclose(
        coords_before[0][:, :3], coords_after[0][:, :3] / rscale, atol=5e-6
    )  # positions
    assert np.allclose(
        coords_before[0][:, 3:], coords_after[0][:, 3:] / vscale, atol=5e-6
    )  # velocities


def shift_snapshot(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rshift: Union[tuple[float, float, float], Annotated[list[float], 3]],
    vshift: Union[tuple[float, float, float], Annotated[list[float], 3]],
):
    if os.path.exists(outfile):
        print(f"{outfile} already exists! removing...")
        os.remove(outfile)

    rshift_str = ",".join(str(item) for item in rshift)
    vshift_str = ",".join(str(item) for item in vshift)

    command = f"snapshift in={filename} out={outfile} rshift={rshift_str} vshift={vshift_str} | tee snapshift_log 2>&1"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


def test_shift(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rshift: Union[tuple[float, float, float], Annotated[list[float], 3]],
    vshift: Union[tuple[float, float, float], Annotated[list[float], 3]],
):
    coords_before = agama.readSnapshot(filename)  # tuple of (xv[N, 6], m[N,])
    coords_after = agama.readSnapshot(outfile)

    assert np.allclose(
        coords_before[0][:, :3], coords_after[0][:, :3] - np.array(rshift), atol=5e-6
    )  # positions
    assert np.allclose(
        coords_before[0][:, 3:], coords_after[0][:, 3:] - np.array(vshift), atol=5e-6
    )  # velocities


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transform snapshot: change units (pc -> kpc) and shift snapshot data."
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
    filename_scaled = args.nemo_file.replace(".nemo", "_scaled.nemo")
    filename_shifted = filename_scaled.replace(".nemo", "_shifted.nemo")

    scale_snapshot(
        filename=args.nemo_file,
        outfile=filename_scaled,
        rscale=r_scale,
        vscale=v_scale,
        mscale=m_scale,
    )
    if args.test:
        test_scale(
            filename=args.nemo_file,
            outfile=filename_scaled,
            rscale=r_scale,
            vscale=v_scale,
            mscale=m_scale,
        )

    shift_snapshot(
        filename=filename_scaled,
        outfile=filename_shifted,
        rshift=args.r_shift,
        vshift=args.v_shift,
    )
    if args.test:
        test_shift(
            filename=filename_scaled,
            outfile=filename_shifted,
            rshift=args.r_shift,
            vshift=args.v_shift,
        )

    # Read nemo file to get the number of particles
    xv, masses = agama.readSnapshot(args.nemo_file)
    (N,) = masses.shape

    # Compute `eps`, `kmax` and dynamical time for gyrFalcON evolution in N-body units
    r_nbody = args.plummer_r / 1000  # in kpcs
    m_nbody = np.sum(masses)
    phi0 = -m_nbody * Grav / r_nbody  # Plummer potential at zero

    eps, kmax, t_dyn = compute_gyrfalcon_parameters(N=N, r0=r_nbody, phi0=phi0)

    out_snap_file = filename.parent / "out_MW.nemo"

    print("*" * 10, "Transformation finished!", "*" * 10)
    print("Run this to start cluster evolution in N-body units for 1 dynamical time:")
    print(
        f"\tgyrfalcON {filename_shifted} {out_snap_file} logstep=300 "
        f"eps={eps} kmax={kmax} tstop={t_dyn} step={t_dyn / 100} Grav={Grav}"
    )
