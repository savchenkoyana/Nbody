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


def remove(file: str, print_msg: Optional[str] = None):
    if os.path.exists(file):
        if print_msg:
            print(print_msg)
        os.remove(file)


class RemoveFileOnEnterExit:
    """Context manager that removes file on enter and (optional) on exit."""

    def __init__(self, file_path, remove_on_exit=True):
        self.file_path = file_path
        self.remove_on_exit = remove_on_exit

    def __enter__(self):
        # Remove the file on enter
        remove(self.file_path, f"Removed file: {self.file_path} on enter.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Remove the file on exit
        if self.remove_on_exit:
            remove(self.file_path, f"Removed file: {self.file_path} on exit.")


def parse_nemo(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    transpose: bool = True,
    remove_artifacts: bool = True,
) -> np.array:
    """Get a np.array with particles for a given NEMO snapshot and time."""
    filename = str(filename)
    snapfile = filename.replace(".nemo", f"{t}.txt")

    with RemoveFileOnEnterExit(snapfile, remove_artifacts):
        command = f"s2a in={filename} out={snapfile} times={t}"
        subprocess.check_call(command, shell=True)
        result = np.loadtxt(snapfile).T if transpose else np.loadtxt(snapfile)

    return result


def profile_by_snap(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    projvector: Optional[_PROJ_VECTOR_TYPE] = None,
    remove_artifacts: bool = True,
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
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    Returns
    -------
    np.ndarray, the first row of which is distance and the second row is density
    """
    if projvector and len(projvector) != 3:
        raise RuntimeError(f"`projvector` should have len == 3, got {projvector}")

    manipname = "sphereprof" if not projvector else "projprof"

    filename = str(filename)
    manipfile = filename.replace(".nemo", f"_{manipname}{t}")

    with RemoveFileOnEnterExit(manipfile, remove_artifacts):
        manippars = "" if not projvector else ",".join([str(_) for _ in projvector])
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

        result = np.loadtxt(manipfile).T

    return result


def lagrange_radius_by_snap(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    fraction: Union[float, str] = 0.5,
    remove_artifacts: bool = True,
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
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    Returns
    -------
    """
    manipname = "lagrange"

    filename = str(filename)
    manipfile = filename.replace(".nemo", f"_{manipname}{t}")

    with RemoveFileOnEnterExit(manipfile, remove_artifacts):
        command = f'manipulate in={filename} out=. manipname=centre_of_mass+{manipname} manippars=";{fraction}" manipfile=";{manipfile}" times={t} | tee {manipname}_log 2>&1'
        print(command)

        subprocess.check_call(command, shell=True)
        result = np.loadtxt(manipfile)[0].T  # dummy fix

    return result
