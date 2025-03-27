"""Parses NbodyX input to give human-readable summary.

Only Nbody6 (without GPU) is now supported. Warning, created using vibe-
coding!
"""

import argparse

kz_descriptions = {
    1: "COMMON save unit 1 (=1: 'touch STOP'; =2: every 100*NMAX steps).",
    2: "COMMON save unit 2 (=1: at output; =2: restart if DE/E > 5*QE).",
    3: "Basic data unit 3 at output time (unformatted, frequency NFIX; =1/2: standard and tail; =3: tail only; >3: cluster + tail).",
    4: "Binary diagnostics on unit 4 (# threshold levels = KZ(4) < 10); (suppressed in input.f & ksint.f); new usage: number of NS & BH on unit #4; >1: BH mass histogram.",
    5: "Initial conditions (#22 =0; =0: uniform & isotropic sphere); =1: Plummer; =2: two Plummer models in orbit, extra input; =3: massive perturber and planetesimal disk, extra input; =4: massive initial binary, extra input: A, E, M1, M2; =5: Jaffe model; >=6: Zhao BH cusp model, extra input if #24 < 0: ZMH, RCUT.",
    6: "Soft & regularized binaries & individual bodies at main output; =1: soft & regularized binaries on unit 6; =2: regularized binaries only; >2: individual bodies (loop from 1 to KZ(6)).",
    7: "Lagrangian radii (>0: RSCALE; =2, 3, 4: output units 6, 7); >=2: half-mass radii of 50% mass, also 1% heavies, unit 6; >=2: Lagrangian radii for two mass groups on unit 31 & 32; >=2: geometric radii for three mass groups on unit 6; =5: density, rms velocity & mean mass on unit 26, 27 & 36; =6: pairwise values of mean mass and radii on unit 28.",
    8: "Primordial binaries (=1 & >=3 routine BINPOP; >=3: SWEEP; =4: Kroupa 1995 period distribution; >4: standard setup using RANGE & SEMI0).",
    9: "Binary output  (=1, 2, 3 in BINDAT): =1: regularized binaries on OUT9; >1: hierarchical systems on HIDAT (NMERGE > 0); =2: regularized and soft binaries (unit #19); =3: soft binaries only on #19.",
    10: "Diagnostic KS output (>0: begin KS; >1: end; >=3: each step).",
    11: "Algorithmic Chain regularization and post-Newtonian (NBODY7). non-zero: PN for unpert KS or re-init ARChain (ksint.f); > 0: addition of initial BHs (binary/singles; scale.f); = -1: standard case of subsystem for ARChain (ksint.f); < -1: ARChain restricted to BH binary components (ksint.f).",
    12: "HR diagnostics of evolving stars (> 0; interval DTPLOT); =2: input of stellar parameters on fort.12 (routine INSTAR).",
    13: "Interstellar clouds (=1: constant velocity; >1: Gaussian).",
    14: "External force (=1: standard tidal field; =2: point-mass galaxy; =3: point-mass + bulge + disk + halo + Plummer; =4: Plummer).",
    15: "Triple, quad, chain (#30 > 0) or merger search (>1: more output).",
    16: "Updating of regularization parameters (>0: RMIN, DTMIN & ECLOSE); >1: RMIN expression based on core radius; >2: modify RMIN for GPERT > 0.05 or < 0.002 in chain.",
    17: "Modification of ETAI, ETAR (>=1) and ETAU (>1) by tolerance QE.",
    18: "Hierarchical systems (=1: diagnostics; =2: primordial; =3: both).",
    19: "Mass loss (=1: old supernova scheme; =3: Eggleton, Tout & Hurley; >3: extra diagnostics).",
    20: "Initial mass function (=0: Salpeter type using ALPHAS; =1: Scalo; =2, 4: Kroupa 1993; =3, 5: Eggleton; > 1: primordial binaries; =6, 7: Kroupa 2001; binary correlated m1/m2, also brown dwarfs. Note: Use PARAMETER (MAXM=1) for setting BODY(1) = BODY10). KGT93 (Kroupa, Gilmore & Tout 1993) not recommended.",
    21: "Extra output (>0: MODEL #, TCOMP, DMIN, AMIN; >1: NESC by JACOBI).",
    22: "Initial m, r, v on #10 (=1: output; >=2: input; >2: no scaling; =2: m, r, v on #10 in any units; scaled to standard units; Note: choose #20 = 0 to avoid Salpeter IMF with scaling; =3: no scaling of input read on fort.10; =4: input from mcluster.c (no scaling; binaries if NBIN0 >0); =-1: astrophysical input (M_sun, km/s, pc) on unit #10).",
    23: "Escaper removal (>1: diagnostics in file ESC with V_inf in km/s); >=3: initialization & integration of tidal tail.",
    24: "Initial conditions for subsystem (M,X,V routine SCALE; KZ(24)= #); <0: ZMH & RCUT (N-body units) Zhao model (#5>=6).",
    25: "Velocity kicks for white dwarfs (=1: type 11 & 12; >1: all WDs).",
    26: "Slow-down of two-body motion (>=1: KS; >=2: chain; =3: rectify).",
    27: "Tidal effects (=1: sequential; =2: chaos; =3: GR energy loss); =-1: collision detector, no coalescence, #13 < 0.",
    28: "GR radiation for NS & BH binaries (with #19 = 3; choice of #27); =4 and #27 = 3: neutron star capture (instar.f).",
    29: "Boundary reflection for hot system (suppressed).",
    30: "Multiple regularization (=1: all; >1: BEGIN/END; >2: each step); =-1: CHAIN only; =-2: TRIPLE & QUAD only.",
    31: "Centre of mass correction after ADJUST (don't use with #23 = 0).",
    32: "Increase output intervals & SMAX based on single particle energy.",
    33: "Histograms at main output (>=1: STEP; =2: STEPR, NBHIST & BINARY).",
    34: "Roche-lobe overflow (=1: ROCHE & SYNCH; =2: ROCHE & BSE synch).",
    35: "Time offset (global time from TTOT = TIME + TOFF; offset = 100).",
    36: "Step reduction for hierarchical systems (suppressed).",
    37: "Neighbour additions in CHECKL (>0: high-velocity; >1: all types).",
    38: "Force polynomial corrections.",
    39: "No unique density centre.",
    40: "Neighbour number control.",
    41: "Pre-mainsequence stellar evolution.",
    42: "Kozai diagnostics.",
    43: "Small velocity kick after GR coalescence.",
    44: "Plotting file for main cluster parameters.",
    45: "Plotting file for BH.",
    46: "Reserved for data analysis.",
    50: "Not used.",
}


def parse_input_file(filename):
    with open(filename) as file:
        lines = [line.strip() for line in file if line.strip()]

    data = {}

    lines = [line.replace("D", "E") for line in lines]

    data["KSTART"], data["TCOMP"] = map(float, lines[0].split())
    (
        data["N"],
        data["NFIX"],
        data["NCRIT"],
        data["NRAND"],
        data["NNBMAX"],
        data["NRUN"],
    ) = map(int, lines[1].split())

    (
        data["ETAI"],
        data["ETAR"],
        data["RS0"],
        data["DTADJ"],
        data["DELTAT"],
        data["TCRIT"],
        data["QE"],
        data["RBAR"],
        data["ZMBAR"],
    ) = map(float, lines[2].split())

    kz_flat_list = [list(map(int, line.split())) for line in lines[3:8]]
    data["KZ"] = [kz for sublist in kz_flat_list for kz in sublist]

    (
        data["DTMIN"],
        data["RMIN"],
        data["ETAU"],
        data["ECLOSE"],
        data["GMIN"],
        data["GMAX"],
    ) = map(float, lines[8].split())

    (
        data["ALPHA"],
        data["BODY1"],
        data["BODYN"],
        data["NBIN0"],
        data["NHI0"],
        data["ZMET"],
        data["EPOCH0"],
        data["DTPLOT"],
    ) = map(float, lines[9].split())

    (data["Q"], data["VXROT"], data["VZROT"], data["RTIDE"], data["SMAX"]) = map(
        float, lines[10].split()
    )

    # TODO: parse next lines!

    return data


def print_results(data):
    print("Non-zero KZ parameters:")
    for i, value in enumerate(data["KZ"], start=1):
        if value != 0:
            meaning = kz_descriptions.get(i, "Unknown KZ option")
            print(f"  KZ{i}: {value} ({meaning})")

    print("\nOther parameters:")
    for key, value in data.items():
        if key != "KZ":
            print(f"  {key}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse an input file and extract relevant parameters."
    )
    parser.add_argument("filename", type=str, help="Path to the input file")
    parser.add_argument(
        "--version",
        type=str,
        choices=["nbody6", "nbody6++gpu", "nbody4"],
        default="nbody6",
        help="Specify the version of the software",
    )

    args = parser.parse_args()

    if args.version not in ["nbody6"]:
        raise NotImplementedError(f"Version '{args.version}' is not implemented yet.")

    data = parse_input_file(args.filename)
    print_results(data)
