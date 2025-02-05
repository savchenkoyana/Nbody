"""Postprocess snapshot: remove source of filed, change length units."""

import argparse
import os
import subprocess
from pathlib import Path
from typing import Union

import numpy as np
from utils.snap import parse_nemo
from utils.snap import remove


def postprocess(
    filename: Union[str, os.PathLike, Path],
    output_file: Union[str, os.PathLike, Path],
    remove_point_source: bool = False,
    source_mass: float = 4.37 * 10**10,
    r_scale: float = 1.0,
    m_scale: float = 1.0,
):
    """
    Postprocess snapshot: remove source of field (if needed) and change length units.
    See https://teuben.github.io/nemo/man_html/snapmask.1.html and
    https://teuben.github.io/nemo/man_html/snapscale.1.html
    """
    # Sanity checks
    if not Path(filename).exists():
        raise RuntimeError(f"filename {filename} does not exist")
    if source_mass <= 0:
        raise RuntimeError(f"Source mass should be positive, got {source_mass} Msun")

    remove(output_file)

    snap = parse_nemo(filename=filename, t=0, transpose=False)
    masses, xv = snap[:, 0], snap[:, 1:7]  # Shapes: [N,] and [N, 6]
    (N,) = masses.shape

    # Remove source mass (optional)
    if remove_point_source:
        assert np.allclose(xv[-1], np.zeros((1, 6)), atol=1e-7), xv[-1]
        assert np.isclose(masses[-1], source_mass / m_scale), (
            masses[-1],
            source_mass / m_scale,
        )

        command = f"snapscale in={filename} out=- rscale={r_scale} mscale={m_scale} | snapmask - {output_file} select=0:{N - 2}"
    else:
        command = f"snapscale in={filename} out={output_file} rscale={r_scale} mscale={m_scale}"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Postprocess snapshot: change units (kpc -> pc). "
        "Optional: remove point source of field."
    )
    parser.add_argument(
        "--snap-file",
        type=str,
        required=True,
        help="Snapshot file (could be any format supported by NEMO's 's2a')",
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
    parser.add_argument(
        "--nbody",
        action="store_true",
        help="Whether to use units for Nbody",
    )
    args = parser.parse_args()

    filename = args.snap_file
    filename_parts = filename.split(".")
    filename_name, filename_ext = filename_parts[:-1], filename_parts[-1]
    output_file = ".".join(filename_name) + "_postprocessed." + filename_ext

    postprocess(
        filename=filename,
        remove_point_source=args.remove_point_source,
        source_mass=args.source_mass,
        r_scale=1e3,  # kpc -> pc
        m_scale=232533.73313343327 if args.nbody else 1.0,
        output_file=output_file,
    )
