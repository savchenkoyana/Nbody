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
import scipy
import scipy.integrate as integrate


def set_units():
    # choose the best units for this task
    # for units explanation see
    # https://physics.stackexchange.com/questions/162966/units-in-gravitational-n-body-simulations
    agama.setUnits(
        length=0.001,
        mass=1,
        velocity=1,
    )  # length in pc, mass in solar mass, velocity in km/s


def create_argparse(description=""):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--N",
        type=int,
        default=10_000,
        help="How many particles to generate. Should be 0 < N <= 10**7. Default: 10_000",
    )
    parser.add_argument(
        "--mu",
        type=float,
        default=0,
        help="Parameter `mu` used for scaling in mass spectrum: y = (x - mu) / s. Units: Solar masses. Default: 0",
    )
    parser.add_argument(
        "--scale",
        "--s",
        type=float,
        default=1,
        help="Parameter `s` used for scaling in mass spectrum: y = (x - mu) / s. Units: Solar masses. Default: 1",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=1,
        help="Std of the log-normal distribution in mass spectrum (dimensionless). Default: 1",
    )
    parser.add_argument(
        "--plummer-r",
        "--r",
        type=float,
        default=10,
        help="Plummer sphere radius (in pc). Default: 10",
    )
    return parser


def check_parameters(args):
    if not (0 < args.N <= 10**7):
        sys.exit(f"Got invalid N={args.N}, should be 0 < N <= 10**7")
    if args.mu < 0:
        sys.exit(
            f"Got invalid mu={args.mu} of the mass spectrum, should not be negative"
        )
    if args.sigma <= 0:
        sys.exit(
            f"Got invalid sigma={args.sigma} of the mass spectrum, should be positive"
        )
    if args.scale <= 0:
        sys.exit(f"Got invalid s={args.scale} of the mass spectrum, should be positive")


def create_self_consistent_model(
    n_iterations: int,
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

        plt.show()

    return scm


def plot_density(
    dens: agama.Density,
    save_path: typing.Optional[typing.Union[str, os.PathLike]] = None,
):
    r = np.logspace(-4, 1)
    xyz = np.vstack((r, r * 0, r * 0)).T

    plt.plot(r, dens(xyz), linestyle="dotted")

    plt.xlabel("r, pc")
    plt.ylabel(r"$\rho, M_\odot / pc^3$")
    plt.xscale("log")
    plt.yscale("log")

    if isinstance(save_path, (str, Path)):
        plt.savefig(Path(save_path))

    plt.show()


def plot_density_diff(
    orig_dens: agama.Density,
    dens: agama.Density,
    save_path: typing.Optional[typing.Union[str, os.PathLike]] = None,
):
    r = np.logspace(-4, 1)
    xyz = np.vstack((r, r * 0, r * 0)).T

    plt.plot(r, np.abs(dens(xyz) - orig_dens(xyz)))

    plt.xlabel("r, pc")
    plt.ylabel(r"$\delta\rho, M_\odot / pc^3$")
    plt.xscale("log")
    plt.yscale("log")

    if isinstance(save_path, (str, Path)):
        plt.savefig(Path(save_path))

    plt.show()


def mass_pdf(x, mu, scale, sigma):
    """Lognormal distribution PDF."""
    # y = (x - mu) / scale
    # return np.exp(-(np.log(y) ** 2) / (2 * sigma**2)) / (np.sqrt(2 * np.pi) * sigma * x)
    return scipy.stats.lognorm.pdf(x, loc=mu, scale=scale, s=sigma)


def compute_mean_mass(mu: float, scale: float, sigma: float) -> float:
    """Compute E[x] of mass pdf analytically or numerically depending on
    parameter values."""
    if mu == 0 and scale == 1:  # Simple case of log-normal distribution with zero mean
        # Calculate E[x] according to analytic formula (see https://en.wikipedia.org/wiki/Log-normal_distribution)
        mass_math_expectation = np.exp(sigma**2 / 2)
    else:  # compute numerically
        pdf = partial(mass_pdf, mu=mu, sigma=sigma, scale=scale)
        norm_, _ = integrate.quad(func=pdf, a=mu, b=np.inf)
        integral_, _ = integrate.quad(func=lambda x: x * pdf(x), a=mu, b=np.inf)
        mass_math_expectation = integral_ / norm_

    return mass_math_expectation


def generate_snap(
    galaxy_model: agama.GalaxyModel,
    N: int,
    generate_mass: typing.Callable[int, list[float]],
) -> typing.Tuple[np.array, np.array]:
    """Generate snapshot with `N` particles. Coordinates and velocities are generated
    according to `galaxy_model`, and masses are generated according to `generate_mass` function.
    """
    # Generate positions and velocities
    snap_xv, snap_m = galaxy_model.sample(args.N)

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

    return (snap_xv, (*masses,))


def compute_gyrfalcon_parameters(
    N: int,
    r0: float,
    phi0: float,
    eta: float = 0.5,
):
    """Compute optimal parameters for gyrFalcON the same way as in https://td.lpi.ru/~eugvas/nbody/tutor.pdf."""
    eps = r0 / N ** (1 / 3)

    v_esc = math.sqrt(-2.0 * phi0)
    t_dyn = r0 / v_esc

    tau = eta * eps / v_esc
    kmax = int(
        0.5 - math.log2(tau)
    )  # tau = 2**(-kmax), 0.5 is for rounding to upper bound

    print(f"Dynamical time for the system: {t_dyn:.3f}")

    return eps, kmax, t_dyn


if __name__ == "__main__":
    parser = create_argparse(
        description="This program creates initial conditions for N-body evolution. "
        "For parameter definition see https://arxiv.org/pdf/2405.06391v1"
    )
    parser.add_argument(
        "--n-iterations",
        type=int,
        default=15,
        help="Number of iterations to create a self-consistent model. Default: 15",
    )
    args = parser.parse_args()
    check_parameters(args)  # sanity checks

    save_dir = Path(
        f"snap_mu{args.mu}_s{args.scale}_sigma{args.sigma}_r{args.plummer_r}_N{args.N}"
    )
    if save_dir.exists():
        shutil.rmtree(save_dir)
    save_dir.mkdir()

    # Set Agama units
    set_units()

    # Compute total mass for the distribution by multiplying the number of samples by E[x] of distribution
    mass_math_expectation = compute_mean_mass(
        mu=args.mu, scale=args.scale, sigma=args.sigma
    )
    m_tot = args.N * mass_math_expectation

    potential = agama.Potential(
        type="Plummer",
        mass=m_tot,
        scaleRadius=args.plummer_r,
    )
    df = agama.DistributionFunction(type="QuasiSpherical", potential=potential)

    scm = create_self_consistent_model(
        n_iterations=args.n_iterations,
        potential=potential,
        df=df,
        verbose=True,
        plot=True,
        save_dir=save_dir,
    )

    # plot density of the resulting model
    plot_density(
        dens=scm.potential.density,
        save_path=save_dir / "scm_density.png",
    )

    # plot the difference between the resulting density and the original density
    plot_density_diff(
        orig_dens=potential.density,
        dens=scm.potential.density,
        save_path=save_dir / "density_diff.png",
    )

    # save the final density/potential profile
    scm.potential.export(str(save_dir / "scm.ini"))

    # create and write out an N−body realization of the model
    gm = agama.GalaxyModel(
        potential=scm.potential,
        df=scm.components[0].df,
        af=scm.af,
    )

    generate_lognorm = lambda x: scipy.stats.lognorm.rvs(
        size=x, loc=args.mu, scale=args.scale, s=args.sigma
    )

    snap = generate_snap(galaxy_model=gm, N=args.N, generate_mass=generate_lognorm)

    in_snap_file = str(save_dir / "IC.nemo")
    out_snap_file = str(save_dir / "out.nemo")
    agama.writeSnapshot(in_snap_file, snap, "nemo")

    print("*" * 10, "Generation finished!", "*" * 10)

    eps, kmax, t_dyn = compute_gyrfalcon_parameters(
        N=args.N,
        r0=args.plummer_r,
        phi0=scm.potential.potential(0, 0, 0),
    )

    print(f"Run this to start cluster evolution for 1 dynamical time:")
    print(
        f"\tgyrfalcON {in_snap_file} {out_snap_file} logstep=300 "
        f"eps={eps} kmax={kmax} tstop={t_dyn} step={t_dyn / 100} Grav={agama.G}"
    )
