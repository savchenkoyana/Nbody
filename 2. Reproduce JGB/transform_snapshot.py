"""Transform snapshot from one units to another."""

import subprocess
import typing
from pathlib import Path

from create_ic import compute_gyrfalcon_parameters


def scale_snapshot(
    filename: typing.Union[str, Path],
    outfile: typing.Union[str, Path],
    rscale: float,
    vscale: float,
    mscale: float,
):
    command = f"snapscale in={filename} out={outfile} rscale={rscale} vscale={vscale} mscale={mscale} | tee snapscale_log 2>&1"
    subprocess.check_call(command, shell=True)


def shift_snapshot(
    filename: typing.Union[str, Path],
    outfile: typing.Union[str, Path],
    rshift: typing.Tuple[float, float, float],
    vshift: typing.Tuple[float, float, float],
):
    rshift_str = ",".join(rshift)
    vshift_str = ",".join(vshift)

    command = f"snapshift in={filename} out={outfile} rshift={rshift_str} vshift={vshift_str} | tee snapshift_log 2>&1"
    subprocess.check_call(command, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transforms snapshot from one units to another."
    )
    parser.add_argument(
        "--nemo-file",
        type=str,
        required=True,
        help="Snapshot file in nemo format",
    )
    parser.add_argument(
        "--r-scale",
        type=float,
        default=1.0,
        help="Scale coefficient for distances",
    )
    parser.add_argument(
        "--v-scale",
        type=float,
        default=1.0,
        help="Scale coefficient for velocities",
    )
    parser.add_argument(
        "--m-scale",
        type=float,
        default=1.0,
        help="Scale coefficient for masses",
    )
    parser.add_argument(
        "--r-shift",
        type=float,  # TODO: vector
        default=0.0,
        help="Shift for distances",
    )
    parser.add_argument(
        "--v-shift",
        type=float,  # TODO: vector
        default=1.0,
        help="Shift for velocities",
    )
    parser.add_argument(
        "--plummer-r",
        "--r",
        type=float,
        default=10,
        help="Plummer sphere radius (in pc). Default: 10",
    )
    args = parser.parse_args()

    # Sanity checks
    if args.v_scale <= 0 or args.r_scale <= 0 or args.m_scale <= 0:
        raise RuntimeError("All coefficients for scaling should be positive!")

    filename = Path(args.nemo_file)
    if not filename.exists():
        raise RuntimeError(f"filename {filename} does not exist")

    # Read nemo file to get the number of particles
    xv, masses = agama.readSnapshot(args.nemo_file)
    (N,) = masses.shape

    # Transform snapshot
    filename_scaled = args.nemo_file.replace(".nemo", "_scaled.nemo")
    filename_shifted = filename_scaled.replace(".nemo", "_shifted.nemo")

    scale_snapshot(
        filename=args.nemo_file,
        outfile=filename_scaled,
        rscale=args.r_scale,
        vscale=args.v_scale,
        mscale=args.m_scale,
    )

    shift_snapshot(
        filename=filename_scaled,
        outfile=filename_shifted,
        rshift=args.rshift,
        vshift=args.vshift,
    )

    # Compute `eps`, `kmax` and dynamical time for gyrFalcON evolution in N-body units
    r_nbody = args.plummer_r / 1000  # in kpc
    m_nbody = np.sum(masses) / 232500  # in 232500 Msun

    eps, kmax, t_dyn = compute_gyrfalcon_parameters(
        N=N, r0=r_nbody, phi0=-m_nbody / r_nbody
    )

    out_snap_file = filename.parent / "out_nbody_units.nemo"

    print("*" * 10, "Transformation finished!", "*" * 10)
    print("Run this to start cluster evolution:")
    print(
        f"\tgyrfalcON {filename_shifted} {out_snap_file} logstep=300 "
        f"eps={eps} kmax={kmax} tstop={3 * t_dyn:.3f} step={t_dyn / 100:.3f}"
    )
