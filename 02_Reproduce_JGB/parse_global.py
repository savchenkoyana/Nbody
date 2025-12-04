import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# see full definitions in the documentation of global.30
_COLNAMES = [
    "TIME[NB]",
    "TIME[Myr]",
    "TCR[Myr]",
    "DE",  # relative energy error
    "BE(3)",  # Current total energy
    "RSCALE[PC]",
    "RTIDE[PC]",
    "RDENS[PC]",
    "RC[PC]",
    "RHOD[M*]",
    "RHOM[M*]",
    "MC[M*]",
    "CMAX",
    "<Cn>",  # frequency 1/ST EP weighted averaged neighbor number
    "Ir/R",  # rregular cost (∑ NB/ST EP) over regular cost (N/ ∑ ST EPR)
    "RCM",
    "VCM",
    "AZ",
    "EB/E",
    "EM/E",
    "VRMS",
    "N",
    "NS",
    "NPAIRS",
    "NUPKS",
    "NPKS",
    "NMERGE",
    "MULT",
    "<NB>",
    "NC",
    "NESC",  # Escapers
    "NSTEPI",  # Irregular integration steps
    "NSTEPB",
    "NSTEPR",  # Regular integration steps
    "NSTEPU",  # Regularized integration steps
    "NSTEPT",
    "NSTEPQ",
    "NSTEPC",  # Chain regularization step
    "NBLOCK",
    "NBLCKR",
    "NNPRED",
    "NBCORR",
    "NBFLUX",
    "NBFULL",
    "NBVOID",
    "NICONV",
    "NLSMIN",
    "NBSMIN",
    "NBDIS",
    "NBDIS2",
    "NCMDER",
    "NFAST",
    "NBFAST",
    "NKSTRY",
    "NKSREG",
    "NKSHYP",
    "NKSPER",
    "NKSMOD",
    "NTTRY",
    "NTRIP",
    "NQUAD",
    "NCHAIN",
    "NMERG",
    "NEWHI",
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"Parses global.30 data")
    parser.add_argument(
        "--exp",
        type=str,
        required=True,
        help="Path to directory with global.30 file",
    )
    parser.add_argument(
        "--values",
        type=str,
        required=True,
        help=f"Comma-separated column values to plot. Choose from {_COLNAMES}",
    )
    args = parser.parse_args()

    exp = Path(args.exp)
    df = pd.read_csv(exp / "global.30", sep=r"\s+", skiprows=[0], header=None)
    df.columns = _COLNAMES

    values = {x for x in args.values.split(",")}
    unknown_values = values.difference(_COLNAMES)
    if unknown_values:
        raise ValueError(f"Unknown columns {unknown_values}")

    # plot
    fig = plt.figure(figsize=(9, 6))
    ax = fig.gca()
    ax.set_xlabel(r"Time t [nbody units]")
    ax.grid()
    for val in values:
        plt.plot(df[val], label=val)

    plt.legend()
    plt.show()
