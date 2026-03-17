"""Scripts for snapshot transformations and other manipulations with
snapshots."""

import os
import subprocess
import warnings
from pathlib import Path
from typing import Annotated
from typing import Literal
from typing import Optional
from typing import Union

import numpy as np
import unsio.input as uns_in

# use TIMEFUZZ 1e-6 for snapshots with too frequent outputs (https://github.com/teuben/nemo/issues/162)
_TIMEFUZZ = os.environ.get("TIMEFUZZ")
if _TIMEFUZZ:
    _TIMEFUZZ = float(_TIMEFUZZ)
else:
    warnings.warn("environment variable TIMEFUZZ is not set, using default value 1e-3")
    _TIMEFUZZ = 1e-3

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


def build_snapfile(filename: Union[str, Path], suffix: str) -> str:
    """Build snapshot-related filename based on original file and suffix."""
    base = str(filename).replace(".nemo", "")
    return f"{base}{suffix}"


def parse_nemo(
    filename: Union[str, Path],
    t: Union[float, str],
    transpose: bool = True,
    remove_artifacts: bool = True,
    nearest: bool = True,
) -> np.ndarray:
    """Get a np.ndarray with particles for a given NEMO snapshot and time.

    Parameters
    ----------
    filename : Union[str, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    transpose : bool
        Whether to return transposed result. Default: True.
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    nearest :
        Whether to take the nearest t value. Default: True.
    Returns
    -------
    np.ndarray
        Array with particles with shape [7, N] (if transposed) or [N, 7] (otherwise).
        7 coordinates are: mass, x, y, z, vx, vy, vz.
    """
    snapfile = build_snapfile(filename, f"_{t}")
    timefuzz = "nearest" if nearest else _TIMEFUZZ

    with RemoveFileOnEnterExit(snapfile, remove_artifacts):
        command = (
            f"snaptrim in={filename} out=- times={t} timefuzz={timefuzz} | "
            f"s2a in=- out={snapfile}"
        )
        print(command)
        subprocess.check_call(command, shell=True)
        return np.loadtxt(snapfile).T if transpose else np.loadtxt(snapfile)


def manipulate_snapshot(
    filename: Union[str, Path],
    t: Union[float, str],
    manipname: str,
    manippars: str,
    manipfile: str,
    remove_artifacts: bool = True,
    nearest: bool = True,
) -> np.ndarray:
    """Helper for commands using 'manipulate' on NEMO snapshots."""
    # in case of joined manipulators, all info is stored in the last file
    last_mp = manipfile.split(";")[-1]
    timefuzz = "nearest" if nearest else _TIMEFUZZ

    with RemoveFileOnEnterExit(last_mp, remove_artifacts):
        command = (
            f"snaptrim in={filename} out=- times={t} timefuzz={timefuzz} | "
            f'manipulate in=- out=. manipname={manipname} manippars="{manippars}" '
            f'manipfile="{manipfile}" | tee {manipname}_log 2>&1'
        )
        print(command)
        subprocess.check_call(command, shell=True)
        return np.loadtxt(last_mp).T


def profile_by_snap(
    filename: Union[str, Path],
    t: Union[float, str],
    projvector: Optional[_PROJ_VECTOR_TYPE] = None,
    remove_artifacts: bool = True,
    dens_par: int = 500,
) -> np.ndarray:
    """Get a np.ndarray with density profile for a given snapshot and time.

    Parameters
    ----------
    filename : Union[str, Path]
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
    manippars_binning = (
        "100,0.05"  # minimum bodies in radial bin, minimum bin size in log(r)
    )
    if projvector:
        manippars = ",".join([str(_) for _ in projvector]) + "," + manippars_binning
    else:
        manippars = manippars_binning

    manipfile = build_snapfile(filename, f"_{manipname}{t}")

    # modify if we need to compute density center first
    if dens_par:
        manipname = f"dens_centre+{manipname}"
        manippars = f"{dens_par};{manippars}"
        manipfile = build_snapfile(filename, f"_{manipname}{t}")
        manipfile = f";{manipfile}"

    result = manipulate_snapshot(
        filename=filename,
        t=t,
        manipname=manipname,
        manippars=manippars,
        manipfile=manipfile,
        remove_artifacts=remove_artifacts,
    )

    return result


def lagrange_radius_by_snap(
    filename: Union[str, Path],
    t: Union[float, str],
    fraction: float = 0.5,
    remove_artifacts: bool = True,
    dens_par: int = 500,
) -> np.ndarray:
    """
    Compute a lagrange radius for a given snapshot and time.
    See https://teuben.github.io/nemo/man_html/lagrange_radii.1.html
    for more info.

    Parameters
    ----------
    filename : Union[str, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    fraction : Union[float, str]
        fraction of mass (parameter for lagrange radius evaluation)
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    dens_par :
        Parameter for `dens_centre` (number of neighbours in SPH-like estimation). Default: 500.
    Returns
    -------
    np.ndarray
        Array with two elements: time and lagrange radius.
    """
    if dens_par:
        manipname = "dens_centre+lagrange"
        manippars = f"{dens_par};{fraction}"
        manipfile = build_snapfile(filename, f"_{manipname}{t}")
        manipfile = f";{manipfile}"
    else:
        manipname = "lagrange"
        manippars = str(fraction)
        manipfile = build_snapfile(filename, f"_{manipname}{t}")

    result = manipulate_snapshot(
        filename=filename,
        t=t,
        manipname=manipname,
        manippars=manippars,
        manipfile=manipfile,
        remove_artifacts=remove_artifacts,
    )

    return result


def center_of_snap(
    filename: Union[str, Path],
    t: Union[float, str],
    density_center: bool = False,
    remove_artifacts: bool = True,
    dens_par: int = 500,
) -> np.ndarray:
    """Compute a center-of-mass or density center for a given snapshot.

    Parameters
    ----------
    filename : Union[str, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    density_center : bool
        whether to compute density center instead of center-of-mass. Default: True
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    dens_par :
        Parameter for `dens_centre` (number of neighbours in SPH-like estimation). Default: 500.
    Returns
    -------
    np.ndarray
        Array with the following structure: t, x, y, z, vx, vy, vz.
    """
    if density_center:
        manipname = "dens_centre"
        manippars = str(dens_par)
    else:
        manipname = "centre_of_mass"
        manippars = ""

    manipfile = build_snapfile(filename, f"_{manipname}{t}")

    result = manipulate_snapshot(
        filename=filename,
        t=t,
        manipname=manipname,
        manippars=manippars,
        manipfile=manipfile,
        remove_artifacts=remove_artifacts,
    )

    return result


def masses_in_lagrange_radius(
    filename: Union[str, Path],
    t: Union[float, str],
    remove_artifacts: bool = True,
    dens_par: int = 500,
    fraction: float = 0.5,
) -> tuple[np.ndarray[np.float32], float, np.ndarray[bool]]:
    """Compute which masses of cluster reside inside the lagrange radius.

    Parameters
    ----------
    filename : Union[str, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    dens_par :
        Parameter for `dens_centre` (number of neighbours in SPH-like estimation). Default: 500.
    fraction :
        Fraction of mass used to compute the Lagrange radius. Default: 0.5
    Returns
    -------
    tuple[np.ndarray[np.float32], float, np.ndarray[bool]]
        First element: np.ndarray with all masses from snapshot
        Second element: lagrange radius 50% for the snapshot
        Third element: binary mask for masses
    """
    snap = parse_nemo(filename=filename, t=t)  # m, x, y, z, vx, vy, vz
    masses = snap[0]

    if dens_par:
        # calculate density center
        center = center_of_snap(
            filename=filename,
            t=t,
            density_center=True,
            remove_artifacts=remove_artifacts,
            dens_par=dens_par,
        )  # center_coords : snap_t, x, y, z, vx, vy, vz
        if center.size == 0:
            raise RuntimeError(f"'dens_centre' didn't converge for t={t}")
    else:
        center = np.array([0, 0, 0, 0], dtype=np.float32)

    # calculate lagrange radius
    snap_t, lagrange_r = lagrange_radius_by_snap(
        filename,
        t,
        remove_artifacts=remove_artifacts,
        dens_par=dens_par,
        fraction=fraction,
    )

    # create mask
    dist = np.linalg.norm(snap[1:4].T - center[1:4], axis=1)
    mask = dist < lagrange_r
    print(f"Number of particles for fraction={fraction}: {mask.sum()}")

    return masses, lagrange_r, mask


def generate_timestamps(filename: Union[str, Path]):
    """This generator yields timestamps for a given file.

    Could be very slow!
    """
    fp_uns = uns_in.CUNS_IN(str(filename), float32=True)

    while fp_uns.nextFrame("mxv"):
        yield fp_uns.getData("time")[1]


def get_timestamps(
    filename: Union[str, Path],
    n_timestamps: int = 100,
    default: bool = False,
) -> np.ndarray:
    """Return timestamps for a given file."""
    if not n_timestamps > 0:
        raise RuntimeError(f"n_timestamps should be positive, got {n_timestamps}")

    if default:
        timestamps = np.arange(0, 14_000, 14_000 / n_timestamps)
    else:
        timestamps = [_ for _ in generate_timestamps(filename)]

    if len(timestamps) < n_timestamps:
        return timestamps

    # else filter
    indices = [_ * len(timestamps) // n_timestamps for _ in range(n_timestamps)]
    return np.array(timestamps)[indices]


def find_density_center(
    positions: np.ndarray[float],
    masses: np.ndarray[float],
    k: int = 6,
):
    """Estimates density center by positions[N, 3] and masses[N,] using
    Casertano-Hut algo (note that NEMO uses another one)."""
    tree = cKDTree(positions)
    dists, idxs = tree.query(
        positions, k=k + 1
    )  # distances to k+1 neighbours including self at zero
    rk = dists[:, k]  # k-th neighbor distance (exclude self at index 0)

    # compute rho by k nearest particles
    neigh_idx = idxs[:, 1 : k + 1]
    mass_k = masses[neigh_idx].sum(axis=1)
    rho = mass_k / (4 / 3 * np.pi * rk**3)

    i_max = np.nanargmax(rho)
    return positions[i_max]
