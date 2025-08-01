"""Tools to create cluster's initial conditions."""

import os
import typing
from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np
from utils.plot import show_with_timeout


def create_self_consistent_model(
    n_iterations: int,
    potential: agama.Potential,
    df: agama.DistributionFunction,
    verbose: bool = False,
    plot: bool = False,
    save_dir: typing.Union[str, os.PathLike] = None,
) -> agama.SelfConsistentModel:
    print("Creating a self-consistent model")
    dens = agama.Density(type="Plummer", mass=1.0, scaleRadius=1.0)

    # define the self-consistent model consisting of a single component
    params = dict(rminSph=0.001, rmaxSph=1000.0, sizeRadialSph=40, lmaxAngularSph=0)
    comp = agama.Component(df=df, density=dens, disklike=False, **params)
    scm = agama.SelfConsistentModel(**params)
    scm.components = [comp]

    # prepare visualization
    r = np.logspace(-4.0, 1.0)
    xyz = np.vstack((r, r * 0, r * 0)).T
    if plot:
        plt.plot(r, dens.density(xyz), label="Init density")
        plt.plot(r, potential.density(xyz), label="True density", c="k")[0].set_dashes(
            [4, 4]
        )

    # perform several iterations of self-consistent modelling procedure
    for i in range(n_iterations):
        scm.iterate()
        if verbose:
            print(
                "Iteration %i, Phi(0)=%g, Mass=%g"
                % (i, scm.potential.potential(0, 0, 0), scm.potential.totalMass())
            )
        if plot:
            plt.plot(r, scm.potential.density(xyz), label="Iteration #" + str(i))

    if plot:
        # show the results
        plt.legend(loc="lower left")
        plt.xlabel("r, pc")
        plt.ylabel(r"$\rho, M_\odot / pc^3$")
        plt.xscale("log")
        plt.yscale("log")

        if isinstance(save_dir, (str, Path)):
            plt.savefig(Path(save_dir) / "scm.png")

        show_with_timeout()

    return scm


def generate_snap(
    galaxy_model: agama.GalaxyModel,
    N: int,
    generate_mass: typing.Callable[int, list[float]],
) -> typing.Tuple[np.array, np.array]:
    """Generate snapshot with `N` particles.

    Coordinates and velocities are generated
    according to `galaxy_model`, and masses are generated according to `generate_mass` function.
    """
    # Generate positions and velocities
    snap_xv, snap_m = galaxy_model.sample(N)

    # Generate masses
    (n_samples,) = snap_m.shape
    masses = generate_mass(n_samples)

    m_sum_prev = np.sum(snap_m)
    m_sum = np.sum(masses)
    print("=" * 10)
    print(
        "Change in total mass after changing mass spectrum:",
        np.abs(m_sum - m_sum_prev) / m_sum_prev,
    )

    return (snap_xv, np.array(masses, dtype=np.float32))
