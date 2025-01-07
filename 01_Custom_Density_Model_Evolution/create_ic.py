"""Create initial conditions for gyrFalcON."""

import argparse
import math
import os
import shutil
import sys
import typing
from pathlib import Path

import agama
import matplotlib.pyplot as plt
import numpy as np

# choose the best units for this task
agama.setUnits(
    length=0.001,
    mass=1,
    velocity=1,
)  # length in pc, mass in solar mass, velocity in km/s

# Default density parameters
_R0 = 5e-3
_RCUT = 10


def dist(xyz: np.array, r0: float = _R0, axis=1):
    return np.sqrt(np.sum(xyz**2, axis=axis) + r0**2)


def rho_bh(xyz: np.array, r0: float = _R0, r_cut: float = _RCUT):
    r = dist(xyz, r0=r0)
    return np.e**4.5 * r ** (-2.8) * np.e ** (-r / r_cut)


def rho_dm(xyz: np.array, r0: float = _R0, r_cut: float = _RCUT):
    r = dist(xyz, r0=r0)
    return np.e**5 * r ** (-2.1) * np.e ** (-r / r_cut)


def create_self_consistent_model(
    potential: agama.Potential,
    df: agama.DistributionFunction,
    verbose: bool = False,
    plot: bool = False,
    save_dir: typing.Union[str, os.PathLike] = None,
):
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
    for i in range(10):
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
        plt.xlabel("r")
        plt.ylabel(r"$\rho$")
        plt.xscale("log")
        plt.yscale("log")
        plt.ylim(1e2, 1e16)
        plt.xlim(1e-4, 1e1)

        if isinstance(save_dir, (str, Path)):
            plt.savefig(Path(save_dir) / "scm.png")

        plt.show()

    return scm


def plot_density(dens: agama.Density, save_dir: typing.Union[str, os.PathLike]):
    r = np.logspace(-4, 1)
    xyz = np.vstack((r, r * 0, r * 0)).T

    plt.plot(r, dens(xyz), linestyle="dotted")

    plt.xlabel("r")
    plt.ylabel(r"$\rho$")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlim(1e-4, 1e1)
    plt.ylim(1e2, 1e9)

    if isinstance(save_dir, (str, Path)):
        plt.savefig(Path(save_dir) / "density.png")

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--density-type",
        type=str,
        required=True,
        choices=["BH", "DM"],
        help="Whether to use black hole (BH) density or dark matter (DM) density",
    )
    parser.add_argument(
        "--N",
        type=int,
        default=10_000,
        help="How many particles to generate. Should be 0 < N <= 10**7. Default: 10_000",
    )
    args = parser.parse_args()

    if not (0 < args.N <= 10**7):
        sys.exit(f"Got invalid N={args.N}, should be 0 < N <= 10**7")

    save_dir = Path(args.density_type)
    if save_dir.exists():
        shutil.rmtree(save_dir)
    save_dir.mkdir()

    if args.density_type == "BH":
        density_function = rho_bh
    elif args.density_type == "DM":
        density_function = rho_dm
    else:
        raise RuntimeError(f"Unknown density type {args.density_type}")

    potential = agama.Potential(
        type="Multipole", density=density_function, symmetry="s"
    )
    df = agama.DistributionFunction(type="QuasiSpherical", potential=potential)

    scm = create_self_consistent_model(
        potential=potential,
        df=df,
        verbose=True,
        plot=True,
        save_dir=save_dir,
    )

    # plot density of the resulting model
    plot_density(
        dens=scm.potential.density,
        save_dir=save_dir,
    )

    # save the final density/potential profile
    scm.potential.export(str(save_dir / "scm.ini"))

    # create and write out an N−body realization of the model
    snap = agama.GalaxyModel(
        potential=scm.potential,
        df=scm.components[0].df,
        af=scm.af,
    ).sample(args.N)

    in_snap_file = str(save_dir / "IC.nemo")
    out_snap_file = str(save_dir / "out.nemo")
    agama.writeSnapshot(in_snap_file, snap, "nemo")

    # Compute optimal parameters for gyrFalcON the same way as in https://td.lpi.ru/~eugvas/nbody/tutor.pdf
    eps = (args.N / _R0**3) ** (-1 / 3)  # n ** (-1 / 3)
    v_esc = math.sqrt(-2.0 * potential.potential(0, 0, 0))
    eta = 0.5
    tau = eta * eps / v_esc
    kmax = int(
        0.5 - math.log2(tau)
    )  # tau = 2**(-kmax), 0.5 is for rounding to upper bound
    t_dyn = _RCUT / v_esc
    print(f"Dynamical time for the system: {t_dyn:.3f}")

    print("*" * 10, "Generation finished!", "*" * 10)
    print("Run this to start cluster evolution:")
    print(
        f"\tgyrfalcON {in_snap_file} {out_snap_file} logstep=300 "
        f"eps={eps} kmax={kmax} tstop={3 * t_dyn:.3f} step={t_dyn / 100:.3f} Grav={agama.G}"
    )
