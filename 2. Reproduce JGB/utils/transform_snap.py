"""Scripts for snapshot transformations."""

import os
import subprocess
from pathlib import Path
from typing import Annotated
from typing import Union

import agama
import numpy as np


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
