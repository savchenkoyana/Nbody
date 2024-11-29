"""Scripts for snapshot transformations and other manipulations with
snapshots."""

import os
import subprocess
from pathlib import Path
from typing import Annotated
from typing import Optional
from typing import Union

import numpy as np


def remove(file, do_print=True):
    if os.path.exists(file):
        if do_print:
            print(f"{file} already exists! removing...")
        os.remove(file)


def parse_nemo(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    transpose: bool = True,
) -> np.array:
    """Get a np.array with particles for a given NEMO snapshot and time."""
    filename = str(filename)

    snapfile = filename.replace(".nemo", f"{t}.txt")

    remove(snapfile, do_print=False)

    command = f"s2a in={filename} out={snapfile} times={t}"
    subprocess.check_call(command, shell=True)

    return np.loadtxt(snapfile).T if transpose else np.loadtxt(snapfile)


def profile_by_snap(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    projvector: Optional[
        Union[tuple[float, float, float], Annotated[list[float], 3]]
    ] = None,
) -> np.array:
    """Get a np.array with density profile for a given snapshot and time.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    projvector : Optional[Union[tuple[float, float, float], Annotated[list[float], 3]]]
        If the vector contains only zeros, spherically symmetric density is computed using 'sphereprof'.
        Otherwise calculates the projected density using the vector as a line of sight (see NEMO's 'projprof').
    Returns
    -------
    np.array, the first row of which is distance and the second row is density
    """
    print("DEbug", projvector)
    manipname = "sphereprof" if not projvector else "projprof"
    print(f"Using manipulator {manipname}")

    filename = str(filename)
    manipfile = filename.replace(".nemo", f"_{manipname}{t}")
    remove(manipfile, do_print=False)

    manippars = '""' if not projvector else ",".join([str(_) for _ in projvector])
    print(manippars, "manippars")
    command = f"manipulate in={filename} out=. manipname={manipname} manippars={manippars} manipfile={manipfile} times={t} | tee {manipname}_log 2>&1"
    print(command)

    subprocess.check_call(command, shell=True)

    return np.loadtxt(manipfile).T
