"""Scripts for snapshot transformations and other manipulations with
snapshots."""

import os
import subprocess
from pathlib import Path
from typing import Annotated
from typing import Literal
from typing import Optional
from typing import Union

import numpy as np

_PROJ_VECTOR_TYPE = Union[
    tuple[float, float, float],
    Annotated[list[float], 3],
    np.ndarray[tuple[Literal[3]], np.dtype[np.float32]],
    np.ndarray[tuple[Literal[3]], np.dtype[np.float64]],
]


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
    projvector: Optional[_PROJ_VECTOR_TYPE] = None,
) -> np.array:
    """Get a np.array with density profile for a given snapshot and time.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    projvector :
        List, tuple or np.ndarray of size 3 with float numbers.
        If `projvector` is None, spherically symmetric density is computed using 'sphereprof'.
        Otherwise computes the projected density using `projvector` as a line-of-sight vector (see NEMO's 'projprof').
    Returns
    -------
    np.ndarray, the first row of which is distance and the second row is density
    """
    if projvector and len(projvector) != 3:  # TODO: check dtype too
        raise RuntimeError(f"`projvector` should have len == 3, got {projvector}")

    manipname = "sphereprof" if not projvector else "projprof"

    filename = str(filename)
    manipfile = filename.replace(".nemo", f"_{manipname}{t}")
    remove(manipfile, do_print=False)

    manippars = "" if not projvector else ",".join([str(_) for _ in projvector])
    # command = f'manipulate in={filename} out=. manipname=dens_centre+{manipname} manippars=";{manippars}" manipfile=";{manipfile}" times={t} | tee {manipname}_log 2>&1'
    command = f'manipulate in={filename} out=. manipname=centre_of_mass+{manipname} manippars=";{manippars}" manipfile=";{manipfile}" times={t} | tee {manipname}_log 2>&1'
    print(command)

    subprocess.check_call(command, shell=True)

    # TODO: dummy fix, needs to take care of!
    with open(manipfile) as f:
        lines = f.readlines()

    first_timestamp = True
    with open(manipfile, "w") as f:
        for line in lines:
            if line.startswith("#"):
                if not first_timestamp:
                    break
            else:
                first_timestamp = False
            f.write(line)

    return np.loadtxt(manipfile).T


def lagrange_radius_by_snap(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    fraction: Union[float, str] = 0.5,
) -> np.array:
    """
    Compute a lagrange radius for a given snapshot and time.
    See https://teuben.github.io/nemo/man_html/lagrange_radii.1.html
    for more info.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    fraction : Union[float, str]
        fraction of mass (parameter for lagrange radius evaluation)
    Returns
    -------
    """
    manipname = "lagrange"

    filename = str(filename)
    manipfile = filename.replace(".nemo", f"_{manipname}{t}")
    remove(manipfile, do_print=False)

    # command = f'manipulate in={filename} out=. manipname=dens_centre+{manipname} manippars=";{fraction}" manipfile=";{manipfile}" times={t} | tee {manipname}_log 2>&1'
    command = f'manipulate in={filename} out=. manipname=centre_of_mass+{manipname} manippars=";{fraction}" manipfile=";{manipfile}" times={t} | tee {manipname}_log 2>&1'
    print(command)

    subprocess.check_call(command, shell=True)

    # return np.loadtxt(manipfile).T[:, -1]  # TODO: dummy fix, needs to take care of!
    return np.loadtxt(manipfile).T
