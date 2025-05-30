"""Parses NbodyX input to give human-readable summary.

Warning, created using vibe-coding!
"""

import re


def parse_namelist(filename):
    """Parse a Fortran‐style namelist file."""
    data = {}
    data["KZ"] = []

    # regex to match KEY=VALUE, possibly repeated on one line
    scalar_re = re.compile(r"([A-Za-z]\w*)\s*=\s*([^,/\s]+)")
    # regex to match KZ(start:end)= followed by whitespace-separated values
    kz_re = re.compile(r"KZ\(\s*(\d+)\s*:\s*(\d+)\s*\)\s*=\s*(.*)")

    with open(filename) as f:
        for raw in f:
            line = raw.strip()
            # skip blank and comment lines and lines starting with "&"
            if not line or line.startswith("&") or line.startswith("/"):
                continue

            # First, handle any KZ(...) lines
            m = kz_re.match(line)
            if m:
                i0, i1, rest = m.group(1), m.group(2), m.group(3)
                i0, i1 = int(i0), int(i1)
                # split the rest on whitespace
                vals = rest.strip().split()

                # if a trailing comma, drop it
                if vals[-1].endswith(","):
                    vals[-1] = vals[-1].rstrip(",")
                if vals[-1] == "":
                    vals = vals[:-1]
                # map each position
                expected = i1 - i0 + 1

                if len(vals) != expected:
                    raise ValueError(
                        f"KZ indices {i0}:{i1} expect {expected} values but got {len(vals)}"
                    )
                for offset, v in enumerate(vals):
                    idx = i0 + offset
                    data["KZ"].append(int(v))
                continue

            # Otherwise, pick up all simple KEY=VALUE pairs on the line
            for key, rawval in scalar_re.findall(line):
                # skip KZ here (we already processed them)
                if key.upper().startswith("KZ"):
                    continue
                data[key] = _cast_value(rawval)

    return data


def _cast_value(s):
    """Convert a Fortran‐style literal into Python int/float/string."""
    # strip any trailing commas
    s = s.rstrip(",")
    # string literal?
    if s.startswith("'") and s.endswith("'"):
        return s.strip("'")
    # try int
    try:
        return int(s)
    except ValueError:
        pass
    # try float (including scientific ‘E’)
    try:
        return float(s)
    except ValueError:
        pass
    # fallback to raw string
    return s


def parse_nbody6ppgpu(filename):
    data = {}
    with open(filename) as file:
        lines = [line.strip() for line in file if line.strip()]
    lines = [line.replace("D", "E") for line in lines]

    (
        data["KSTART"],
        data["TCOMP"],
        data["TCRTP0"],
        data["isernb"],
        data["iserreg"],
        data["iserks"],
    ) = map(float, lines[0].split())

    (
        data["N"],
        data["NFIX"],
        data["NCRIT"],
        data["NRAND"],
        data["NNBOPT"],
        data["NRUN"],
        data["NCOMM"],
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
    if len(data["KZ"]) != len(mappings._NBODY6_KZ):
        raise RuntimeError(
            f"KZ length should be {len(mappings._NBODY6_KZ)}, len={len(data['KZ'])} is given"
        )

    (
        data["DTMIN"],
        data["RMIN"],
        data["ETAU"],
        data["ECLOSE"],
        data["GMIN"],
        data["GMAX"],
        data["SMAX"],
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

    (data["Q"], data["VXROT"], data["VZROT"], data["RTIDE"]) = map(
        float, lines[10].split()
    )

    # TODO: parse next lines!
    return data


def parse_nbody6(filename):
    data = {}
    with open(filename) as file:
        lines = [line.strip() for line in file if line.strip()]
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
    if len(data["KZ"]) != len(mappings._NBODY6_KZ):
        raise RuntimeError(
            f"KZ length should be {len(mappings._NBODY6_KZ)}, len={len(data['KZ'])} is given"
        )

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


def parse_nbody4(filename):
    data = {}
    with open(filename) as file:
        lines = [line.strip() for line in file if line.strip()]
    lines = [line.replace("D", "E") for line in lines]

    data["KSTART"], data["TCOMP"], data["GPID"] = map(float, lines[0].split())
    (
        data["N"],
        data["NFIX"],
        data["NCRIT"],
        data["NRAND"],
        data["NRUN"],
    ) = map(int, lines[1].split())

    (
        data["ETA"],
        data["DTADJ"],
        data["DELTAT"],
        data["TCRIT"],
        data["QE"],
        data["RBAR"],
        data["ZMBAR"],
    ) = map(float, lines[2].split())

    kz_flat_list = [list(map(int, line.split())) for line in lines[3:7]]
    data["KZ"] = [kz for sublist in kz_flat_list for kz in sublist]
    if len(data["KZ"]) != len(mappings._NBODY4_KZ):
        raise RuntimeError(
            f"KZ length should be {len(mappings._NBODY4_KZ)}, len={len(data['KZ'])} is given"
        )

    (
        data["DTMIN"],
        data["RMIN"],
        data["ETAU"],
        data["ECLOSE"],
        data["GMIN"],
        data["GMAX"],
    ) = map(float, lines[7].split())

    (
        data["ALPHA"],
        data["BODY1"],
        data["BODYN"],
        data["NBIN0"],
        data["ZMET"],
        data["EPOCH0"],
        data["DTPLOT"],
    ) = map(float, lines[8].split())

    (data["Q"], data["VXROT"], data["VZROT"], data["RTIDE"]) = map(
        float, lines[9].split()
    )

    # Here we only consider point-mass case
    (data["GMG"], data["RG0"]) = map(float, lines[10].split())
    return data


def parse_input_file(filename, version):
    """Parse direct N-body codes inputs.

    Supported versions: Nbody4, Nbody6, Nbody6ppGPU, Nbody6PPGPU-beijing.
    """
    if version == "nbody6":
        return parse_nbody6(filename)
    elif version == "nbody6++gpu":
        return parse_nbody6ppgpu(filename)
    elif version == "nbody6++gpu-beijing":
        try:
            data = parse_nbody6ppgpu(filename)
        except:
            data = parse_namelist(filename)
        return data
    elif version == "nbody4":
        return parse_nbody4(lines)
    else:
        raise NotImplementedError(f"version {version} not implemented")
