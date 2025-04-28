"""This program plots lagrange radii that were computed during the
simulation."""

from pathlib import Path

import matplotlib.pyplot as plt
from utils.general import check_parameters
from utils.general import create_argparse
from utils.plot import create_label
from utils.snap import parse_fort14

if __name__ == "__main__":
    parser = create_argparse(
        description="This program plots lagrange radii that were computed during the simulation."
    )
    parser.add_argument(
        "--fort14-file",
        type=str,
        required=True,
        help="fort.14 file with data",
    )
    parser.add_argument(
        "--timeUnitMyr",
        type=float,
        default=0.97779,
        help="Time unit in Myr. Default: 0.97779",
    )
    parser.add_argument(
        "--lengthUnitPc",
        type=float,
        default=1.0,
        help="Lenght unit in pc. Default: 1.0",
    )
    args = parser.parse_args()

    check_parameters(args)  # sanity checks

    # assuming filenames are: /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>/out.nemo
    # we will save data into /path/to/Nbody/02_Reproduce_JGB/<DIRNAME>
    save_dir = Path(args.fort14_file).parents[0]

    label = create_label(mu=args.mu, scale=args.scale, sigma=args.sigma)

    fig_rt_nbody, ax_rt_nbody = plt.subplots()  # Nbody units
    ax_rt_nbody.set_xlabel("$t$, Nbody units")
    ax_rt_nbody.set_ylabel("Lagrange radius, $Log_{10}(r)$, Nbody units")
    ax_rt_nbody.set_title(f"Lagrange radii for '{save_dir}'")

    fig_rt, ax_rt = plt.subplots()  # Astrophysical units
    ax_rt.set_xlabel("$t$, Gyr")
    ax_rt.set_ylabel("Lagrange radius, pc")
    ax_rt.set_title(f"Lagrange radii for '{save_dir}'")

    if not Path(args.fort14_file).exists():
        raise RuntimeError(f"filename {args.fort14_file} does not exist")

    fraction, data = parse_fort14(args.fort14_file)
    linestyles = ["--", "-.", ":"]

    for i, frac in enumerate(fraction):
        times, lagrange_radii = data[:, 0], data[:, i + 1]
        linestyle = linestyles[i % len(linestyles)]
        ax_rt_nbody.plot(times, lagrange_radii, linestyle, label=f"{int(frac*100)}%")
        ax_rt.plot(
            times * 1e-3 * args.timeUnitMyr,
            args.lengthUnitPc * 10**lagrange_radii,
            linestyle,
            label=f"{int(frac*100)}%",
        )

    ax_rt_nbody.legend()
    ax_rt.legend()

    fig_rt_nbody.savefig(save_dir / "lagrange_radii_nbody.png")
    fig_rt.savefig(save_dir / "lagrange_radii.png")

    plt.show()
