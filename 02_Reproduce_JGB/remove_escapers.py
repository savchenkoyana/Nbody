import argparse
from pathlib import Path

import agama
import numpy as np
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exp",
        type=str,
        required=True,
        help="Directory with files 'global.30' and 'out_scaled.nemo'.",
    )
    args = parser.parse_args()
    exp = Path(args.exp)

    df = pd.read_csv(exp / "global.30", sep=r"\s+", skiprows=[0], header=None)

    colnames = (
        "TIME[NB} TIME[Myr] TCR[Myr] DE BE(3) RSCALE[PC] RTIDE[PC] RDENS[PC] RC[PC] "
        "RHOD[M*] RHOM[M*] MC[M*] CMAX <Cn> Ir/R RCM VCM AZ EB/E EM/E VRMS N NS NPAIRS NUPKS NPKS NMERGE MULT <NB> NC NESC "
        "NSTEPI NSTEPB NSTEPR NSTEPU NSTEPT NSTEPQ NSTEPC NBLOCK NBLCKR NNPRED NBCORR NBFLUX NBFULL NBVOID NICONV NLSMIN "
        "NBSMIN NBDIS NBDIS2 NCMDER NFAST NBFAST NKSTRY NKSREG NKSHYP NKSPER NKSMOD NTTRY NTRIP NQUAD NCHAIN NMERG NEWHI"
    ).split()
    df.columns = colnames

    nemo_file = exp / "out_scaled.nemo"

    with agama.NemoFile(exp / "out_2rtide.nemo", "w") as out:
        for i, snap in enumerate(agama.NemoFile(nemo_file)):
            pos = snap["Position"]
            dist = np.linalg.norm(pos, axis=1)
            mask = dist < 2 * df["RTIDE[PC]"][i]
            print(f"{i}: masked {np.sum(mask)} particles")
            new_snap = {
                key: val[mask] if isinstance(val, np.ndarray) else val
                for key, val in snap.items()
            }

            out.write(new_snap)
