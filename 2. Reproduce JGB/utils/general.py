"""General utils."""

import argparse
import math
import sys
import typing

import agama
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


def create_argparse(description="") -> argparse.ArgumentParser:
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


def mass_pdf(x, mu, scale, sigma) -> typing.Callable[float, float]:
    """Lognormal distribution PDF."""
    # y = (x - mu) / scale
    # return np.exp(-(np.log(y) ** 2) / (2 * sigma**2)) / (np.sqrt(2 * np.pi) * sigma * x)
    return scipy.stats.lognorm.pdf(x, loc=mu, scale=scale, s=sigma)


def compute_mean_mass(mu: float, scale: float, sigma: float) -> float:
    """Compute E[x] of mass pdf analytically or numerically depending on
    parameter values.

    See
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
    for parameters definition.
    """
    if mu == 0 and scale == 1:  # Simple case of log-normal distribution with zero mean
        # Calculate E[x] according to analytic formula (see https://en.wikipedia.org/wiki/Log-normal_distribution)
        mass_math_expectation = np.exp(sigma**2 / 2)
    else:  # compute numerically
        pdf = partial(mass_pdf, mu=mu, sigma=sigma, scale=scale)
        norm_, _ = integrate.quad(func=pdf, a=mu, b=np.inf)
        integral_, _ = integrate.quad(func=lambda x: x * pdf(x), a=mu, b=np.inf)
        mass_math_expectation = integral_ / norm_

    return mass_math_expectation


def compute_gyrfalcon_parameters(
    N: int,
    r0: float,
    phi0: float,
    eta: float = 0.5,
) -> typing.Tuple[float, int, float]:
    """
    Compute optimal parameters for gyrFalcON the same way
    as in https://td.lpi.ru/~eugvas/nbody/tutor.pdf.

    Parameters
    ----------
    N : int
        the number of particles in a snapshot we want to evolve
    r0 :
        characteristic size of a density profile
    phi0 : float
        the value of a particles' potential at (0, 0, 0)
    eta : float, optional
        parameter that regulates precision of evaluation (see tutorial)
    Returns
    -------
    tuple[float, int, float]
        first value -- `eps` parameter for `gyrFalcON`
        second value -- `kmax` parameter for `gyrFalcON`
        third value -- dynamical time of simulation
    """
    eps = r0 / N ** (1 / 3)

    v_esc = math.sqrt(-2.0 * phi0)
    t_dyn = r0 / v_esc

    tau = eta * eps / v_esc
    kmax = int(
        0.5 - math.log2(tau)
    )  # tau = 2**(-kmax), 0.5 is for rounding to upper bound

    print(f"Dynamical time for the system: {t_dyn:.3f}")

    return eps, kmax, t_dyn
