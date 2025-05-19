"""Scale NEMO snapshot to astrophysical units."""

import argparse
from pathlib import Path
from typing import Union

import agama
from utils.nbody6_log import load_scaling
from utils.snap import remove


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
        help="Directory with experiment. It is assumed that there are `out.nemo` and `exp.out`.",
    )
    args = parser.parse_args()
    exp = Path(args.exp)

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
