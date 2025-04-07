"""Scripts for snapshot transformations and other manipulations with
snapshots."""

import math
import os
import subprocess
from pathlib import Path
from typing import Annotated
from typing import Literal
from typing import Optional
from typing import Union

import numpy as np
import unsio.input as uns_in

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
) -> np.ndarray:
    """Get a np.ndarray with particles for a given NEMO snapshot and time.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    transpose : bool
        Whether to return transposed result. Default: True.
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    Returns
    -------
    np.ndarray
        Array with particles with shape [7, N] (if transposed) or [N, 7] (otherwise).
        7 coordinates are: mass, x, y, z, vx, vy, vz.
    """
    filename = str(filename)
    snapfile = filename.replace(".nemo", "") + f"{t}.txt"

    with RemoveFileOnEnterExit(snapfile, remove_artifacts):
        command = f"snaptrim in={filename} out=- times={t} timefuzz=0.000001 | s2a in=- out={snapfile}"
        subprocess.check_call(command, shell=True)
        return np.loadtxt(snapfile).T if transpose else np.loadtxt(snapfile)


def profile_by_snap(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    projvector: Optional[_PROJ_VECTOR_TYPE] = None,
    remove_artifacts: bool = True,
) -> np.ndarray:
    """Get a np.ndarray with density profile for a given snapshot and time.

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
    manipfile = filename.replace(".nemo", "") + f"_{manipname}{t}"

    with RemoveFileOnEnterExit(manipfile, remove_artifacts):
        manippars = "" if not projvector else ",".join([str(_) for _ in projvector])
        command = f'snaptrim in={filename} out=- times={t} timefuzz=0.000001 | manipulate in=- out=. manipname=dens_centre+{manipname} manippars=";{manippars}" manipfile=";{manipfile}" | tee {manipname}_log 2>&1'
        print(command)

        subprocess.check_call(command, shell=True)

        return np.loadtxt(manipfile).T


def lagrange_radius_by_snap(
    filename: Union[str, os.PathLike, Path],
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
    filename : Union[str, os.PathLike, Path]
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
    manipname = "lagrange"

    filename = str(filename)
    manipfile = filename.replace(".nemo", "") + f"_{manipname}{t}"

    with RemoveFileOnEnterExit(manipfile, remove_artifacts):
        if dens_par:
            command = f'snaptrim in={filename} out=- times={t} timefuzz=0.000001 | manipulate in=- out=. manipname=dens_centre+{manipname} manippars="{dens_par};{fraction}" manipfile=";{manipfile}" | tee {manipname}_log 2>&1'
        else:
            command = f'snaptrim in={filename} out=- times={t} timefuzz=0.000001 | manipulate in=- out=. manipname={manipname} manippars="{fraction}" manipfile="{manipfile}" | tee {manipname}_log 2>&1'

        print(command)

        subprocess.check_call(command, shell=True)
        return np.loadtxt(manipfile).T


def center_of_snap(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    density_center: bool = False,
    remove_artifacts: bool = True,
    dens_par: int = 500,
) -> np.ndarray:
    """Compute a center-of-mass or density center for a given snapshot.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
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
    manipname = "dens_centre" if density_center else "centre_of_mass"
    if not density_center:
        dens_par = ""

    filename = str(filename)
    manipfile = filename.replace(".nemo", "") + f"_{manipname}{t}"

    with RemoveFileOnEnterExit(manipfile, remove_artifacts):
        command = f'snaptrim in={filename} out=- times={t} timefuzz=0.000001 | manipulate in=- out=. manipname={manipname} manippars="{dens_par}" manipfile="{manipfile}" | tee {manipname}_log 2>&1'
        print(command)

        subprocess.check_call(command, shell=True)
        return np.loadtxt(manipfile).T


def masses_in_lagrange_radius(
    filename: Union[str, os.PathLike, Path],
    t: Union[float, str],
    remove_artifacts: bool = True,
    dens_par: int = 500,
) -> tuple[np.ndarray[np.float32], float, np.ndarray[bool]]:
    """Compute which masses of cluster reside inside the half-mass radius.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    dens_par :
        Parameter for `dens_centre` (number of neighbours in SPH-like estimation). Default: 500.
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
    )

    # create mask
    dist = np.linalg.norm(snap[1:4].T - center[1:4], axis=1)
    mask = dist < lagrange_r
    print(f"Number of particles for half-mass radius {lagrange_r}: {mask.sum()}")

    return masses, lagrange_r, mask


def generate_timestamps(filename: Union[str, Path]):
    """This generator yields timestamps for a given file."""
    fp_uns = uns_in.CUNS_IN(str(filename), float32=True)

    while fp_uns.nextFrame("mxv"):
        yield fp_uns.getData("time")[1]


def get_timestamps(
    filename: Union[str, Path],
    n_timestamps: int = 100,
) -> np.ndarray:
    """Return timestamps for a given file."""
    if not n_timestamps > 0:
        raise RuntimeError(f"n_timestamps should be positive, got {n_timestamps}")

    timestamps = [_ for _ in generate_timestamps(filename)]

    if len(timestamps) < n_timestamps:
        return timestamps

    # else filter
    indices = [_ * len(timestamps) // n_timestamps for _ in range(n_timestamps)]
    return np.array(timestamps)[indices]


def get_virial(
    filename: Union[str, Path],
    eps: float,
    t: Union[float, str],
    remove_artifacts: bool = True,
):
    """Compute virial ratio and energy for simulation file.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    eps : float
        gravitational softening (use the same as during the simulation)
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    Returns
    -------
    np.ndarray
        Array with columns: time, 2T/W, T+W, T, W_acc, W_phi, W_exact, M
    """
    filename = str(filename)
    virfile = filename.replace(".nemo", "") + f"{t}_vir.txt"

    with RemoveFileOnEnterExit(virfile, remove_artifacts):
        command = f"snaptrim in={filename} out=- times={t} timefuzz=0.000001 | snapvratio - wmode=exact eps={eps} newton=t | tee {virfile}"
        print(command)
        subprocess.check_call(command, shell=True)

        return np.loadtxt(virfile).T


def get_momentum(
    filename: Union[str, Path],
    t: Union[float, str],
    remove_artifacts: bool = True,
):
    """Compute momentum and angular momentum for simulation file.

    Parameters
    ----------
    filename : Union[str, os.PathLike, Path]
        the name of NEMO snapshot file
    t : Union[float, str]
        which time point in snapshot to use for profile calculations
    remove_artifacts :
        Whether to remove artifacts after the function execution. Default: True.
    Returns
    -------
    list
        List with items: pos, x, y, z, vel, vx, vy, vz, l, lx, ly, lz
    """
    filename = str(filename)
    momentum_file = filename.replace(".nemo", "") + f"{t}_momentum.txt"

    with RemoveFileOnEnterExit(momentum_file, remove_artifacts):
        command = f"snaptrim in={filename} out=- times={t} timefuzz=0.000001 | snapkinem - weight=m | tee {momentum_file}"
        print(command)
        subprocess.check_call(command, shell=True)

        result = []

        # parse file
        with open(momentum_file) as f:
            for line in f:
                stripped = line.strip()
                if (
                    stripped.startswith("pos:")
                    or stripped.startswith("vel:")
                    or stripped.startswith("jvec:")
                ):
                    data = [float(x) for x in line.split()[1:]]
                    result.extend(data)
                else:
                    continue
        return result


def count_binaries(
    filename: Union[str, Path],
    t: Union[float, str],
    r_threshold: float,
):
    """Count the number of binaries in snapshot (G=1 is assumed).

    Based on $NEMO/src/nbody/reduc/snapbinary.c
    """
    snap = parse_nemo(filename=filename, t=t)  # m, x, y, z, vx, vy, vz
    N = snap.shape[1]

    binary_counts = 0

    for i in range(N):
        jmin = None
        epot_min = math.inf

        for j in range(N):
            if j == i:
                continue

            dr = np.linalg.norm(snap[1:4, i] - snap[1:4, j])
            dv = np.linalg.norm(snap[4:7, i] - snap[4:7, j])
            m = snap[0, i] + snap[0, j]
            ekin = 0.5 * dv**2
            epot = -m / dr

            if ekin + epot < 0 and epot < epot_min and dr < r_threshold:
                epot_min = epot
                jmin = j

        if jmin is not None and jmin > i:  # TODO: rewrite?
            # print(i, jmin)
            binary_counts += 1

    return binary_counts
