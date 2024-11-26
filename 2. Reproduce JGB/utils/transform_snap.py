"""Scripts for snapshot transformations."""

import os
import subprocess
from pathlib import Path
from typing import Annotated
from typing import Union

import agama
import numpy as np


def remove(file):
    if os.path.exists(file):
        print(f"{file} already exists! removing...")
        os.remove(file)


def scale_snapshot(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rscale: float,
    vscale: float,
    mscale: float,
):
    remove(outfile)

    command = f"snapscale in={filename} out={outfile} rscale={rscale} vscale={vscale} mscale={mscale} | tee snapscale_log 2>&1"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


def shift_snapshot(
    filename: Union[str, Path],
    outfile: Union[str, Path],
    rshift: Union[tuple[float, float, float], Annotated[list[float], 3]],
    vshift: Union[tuple[float, float, float], Annotated[list[float], 3]],
):
    remove(outfile)

    rshift_str = ",".join(str(item) for item in rshift)
    vshift_str = ",".join(str(item) for item in vshift)

    command = f"snapshift in={filename} out={outfile} rshift={rshift_str} vshift={vshift_str} | tee snapshift_log 2>&1"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


def create_center_mass_snapshot(
    outfile: Union[str, Path],
    mass: float,
):
    remove(outfile)

    command = f"echo 0,0,0,0,0,0,{mass} | tabtos - {outfile} nbody=1 block1=x,y,z,vx,vy,vz,m | tee tabtos_log 2>&1"

    print(f"Running:\n\t{command}\n")
    subprocess.check_call(command, shell=True)


def stack_snapshot(
    filename1: Union[str, Path],
    filename2: Union[str, Path],
    outfile: Union[str, Path],
):
    remove(outfile)

    if not os.path.exists(filename1):
        raise FileNotFoundError(f"{filename1} does not exist")
    if not os.path.exists(filename2):
        raise FileNotFoundError(f"{filename2} does not exist")

    command = f"snapstack in1={filename1} in2={filename2} out={outfile} | tee snapstack_log 2>&1"

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


def test_center_mass_snapshot(
    filename: Union[str, Path],
    mass: float,
):
    xv, m = agama.readSnapshot(filename)  # tuple of (xv[1, 6], m[1,])

    assert np.allclose(xv, np.zeros_like(xv))
    assert np.allclose(m, mass)


def test_stack(
    filename1: Union[str, Path],
    filename2: Union[str, Path],
    outfile: Union[str, Path],
):
    xv1, m1 = agama.readSnapshot(filename1)
    xv2, m2 = agama.readSnapshot(filename2)
    xv, m = agama.readSnapshot(outfile)

    assert np.allclose(np.concatenate((xv1, xv2)), xv)
    assert np.allclose(np.concatenate((m1, m2)), m)
