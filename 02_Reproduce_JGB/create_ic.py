"""Create initial conditions for a cluster."""

import shutil
from pathlib import Path

import agama
import scipy
from utils.general import check_parameters
from utils.general import compute_gyrfalcon_parameters
from utils.general import compute_mean_mass
from utils.general import create_argparse
from utils.general import set_units
from utils.ic import create_self_consistent_model
from utils.ic import generate_snap
from utils.plot import plot_density
from utils.plot import plot_density_diff

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
        f"\tgyrfalcON {in_snap_file} {out_snap_file} logstep=3000 "
        f"eps={eps} kmax={kmax} tstop={t_dyn} step={t_dyn / 10} Grav={agama.G}"
    )
