"""Postprocess."""

import argparse
import os
import subprocess
import warnings
from pathlib import Path
from typing import Union

import agama
import numpy as np
from utils.nbody6_log import load_scaling
from utils.snap import parse_nemo
from utils.snap import remove


def remove_point_source(
    filename: Union[str, os.PathLike, Path],
    output_file: Union[str, os.PathLike, Path],
):
    # Sanity checks
    if not Path(filename).exists():
        raise RuntimeError(f"filename {filename} does not exist")

    remove(output_file)

    snap = parse_nemo(filename=filename, t=0, transpose=False)
    masses, xv = snap[:, 0], snap[:, 1:7]  # Shapes: [N,] and [N, 6]
    (N,) = masses.shape

    # Remove source mass
    if not np.allclose(xv[-1], np.zeros((1, 6)), atol=1e-7):
        warnings.warn(f"Source coordinates diverge from zero: {xv[-1]}")

    command = f"snapmask {filename} {output_file} select=0:{N - 2}"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


def scale_snapshot(filename: Union[str, Path], outfile: Union[str, Path], scalings):
    """Transform snapshot values for keys: 'Time', 'Mass', 'Position', 'Velocity', leave others intact."""
    remove(outfile)

    with agama.NemoFile(outfile, "w") as out:
        for i, snap in enumerate(agama.NemoFile(filename)):
            new_snap = snap
            new_snap["Time"] = new_snap["Time"] * scalings["T*"]
            new_snap["Mass"] = new_snap["Mass"] * scalings["M*"]
            new_snap["Position"] = new_snap["Position"] * scalings["R*"]
            new_snap["Velocity"] = new_snap["Velocity"] * scalings["V*"]

            out.write(new_snap)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This programs scales NEMO snapshot to astrophysical units."
    )
    parser.add_argument(
        "--exp",
        type=str,
        required=True,
        help="Two cases:\n"
        "1 --- nbody6++gpu-beijing: Directory with experiment. It is assumed that there are `out.nemo` and `exp.out`."
        "2 --- gyrfalcon: output file with `nemo` extension.",
    )
    parser.add_argument(
        "--version",
        type=str,
        choices=[
            "gyrfalcon",
            "nbody0",
            "nbody1",
            "nbody2",
            "nbody6",
            "nbody6++gpu",
            "nbody6++gpu-beijing",
        ],
        default="nbody6++gpu-beijing",
        help="Specify the version of the software",
    )
    args = parser.parse_args()
    exp = Path(args.exp)

    if args.version.startswith("nbody6"):
        scalings = load_scaling(exp / "exp.out")
        print(
            f"Scale coefficients: R*={scalings['R*']}[pc], V*={scalings['V*']}[km/s], T*={scalings['T*']}[Myr], M*={scalings['M*']}[Msun]"
        )

        # Snapscale
        scale_snapshot(
            filename=exp / "out.nemo",
            outfile=exp / "out_scaled.nemo",
            scalings=scalings,
        )

    elif args.version in ["nbody0", "nbody1", "nbody2"]:
        # simulation units are: pc, ~232 Msun, km/s (G=1)
        scalings = {"R*": 1.0, "M*": 232.5337331, "V*": 1.0, "T*": 0.977792221683525}
        print(
            f"Scale coefficients: R*={scalings['R*']}[pc], V*={scalings['V*']}[km/s], T*={scalings['T*']}[Myr], M*={scalings['M*']}[Msun]"
        )

        filename_parts = str(exp).split(".")
        filename_name, filename_ext = filename_parts[:-1], filename_parts[-1]
        out1 = ".".join(filename_name) + "_astro_units." + filename_ext
        out2 = ".".join(filename_name) + "_postprocessed." + filename_ext

        # Snapscale
        scale_snapshot(
            filename=exp,
            outfile=out1,
            scalings=scalings,
        )

        remove_point_source(out1, out2)

    elif args.version == "gyrfalcon":
        # simulation units are: kpc, Msun, km/s (G~4e-6)
        scalings = {
            "R*": 1e3,
            "M*": 1.0,
            "V*": 1.0,
            "T*": 977.792221683525,
        }
        print(
            f"Scale coefficients: R*={scalings['R*']}[pc], V*={scalings['V*']}[km/s], T*={scalings['T*']}[Myr], M*={scalings['M*']}[Msun]"
        )

        filename_parts = str(exp).split(".")
        filename_name, filename_ext = filename_parts[:-1], filename_parts[-1]
        out1 = ".".join(filename_name) + "_astro_units." + filename_ext
        out2 = ".".join(filename_name) + "_postprocessed." + filename_ext

        # Snapscale
        scale_snapshot(
            filename=exp,
            outfile=out1,
            scalings=scalings,
        )

        remove_point_source(out1, out2)
