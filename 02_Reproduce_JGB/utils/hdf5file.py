"""Load and access Nbody6++GPU HDF5 snapshot data."""

import warnings

import h5py
import numpy as np


class NBodySnapshot:
    """Convenience class to load and access Nbody6++GPU HDF5 snapshot data.

    Parses scalar parameters and particle data (singles and binaries).
    Returns Fortran-style arrays (1-based) to avoid confusion. See
    `src/Main/custom_output_facility.F` for data output details.
    """

    SCALAR_MAP = {
        1: "TTOT",
        2: "NPAIRS",
        3: "RBAR",
        4: "ZMBAR",
        5: "N",
        6: "TSTAR",
        7: "RDENS1",
        8: "RDENS2",
        9: "RDENS3",
        10: "TTOT_TCR0",
        11: "TSCALE",
        12: "VSTAR",
        13: "RC",
        14: "NC",
        15: "VC",
        16: "RHOM",
        17: "CMAX",
        18: "RSCALE",
        19: "RSMIN",
        20: "DMIN1",
        21: "RG1",
        22: "RG2",
        23: "RG3",
        24: "VG1",
        25: "VG2",
        26: "VG3",
        27: "TIDAL1",
        28: "TIDAL2",
        29: "TIDAL3",
        30: "TIDAL4",
        31: "GMG",
        32: "OMEGA",
        33: "DISK",
        34: "A_OORT",
        35: "B_OORT",
        36: "ZMET_HURLEY",
        **{i + 37: f"ZPAR{i+1}" for i in range(20)},  # ZPARS1-20 begin at index 37
        57: "ETAI",
        58: "ETAR",
        59: "ETAU",
        60: "ECLOSE",
        61: "DTMIN",
        62: "RMIN",
        63: "GMIN",
        64: "GMAX",
        65: "SMAX",
        66: "NNBOPT",
        67: "EPOCH0",
        68: "N_SINGLE",
        69: "N_BINARY",
        70: "N_MERGER",
    }

    def __init__(self, filepath):
        warnings.warn(
            "Uses Fortran-style (1-based) array for convenience. Data at index 0 is always empty!"
        )
        self.filepath = filepath
        self._load_file()
        self._parse_scalars()
        self._parse_particles()

    def _load_file(self):
        self._f = h5py.File(self.filepath, "r")
        self.step = next(iter(self._f.keys()))
        self.group = self._f[self.step]

    def _parse_scalars(self):
        raw = self.group["000 Scalars"][:]

        S = np.zeros(len(raw) + 1)
        S[1:] = raw

        self.scalars = {name: S[idx] for idx, name in self.SCALAR_MAP.items()}
        self.TTOT = self.scalars["TTOT"]
        self.NPAIRS = int(self.scalars["NPAIRS"])
        self.N = int(self.scalars["N"])
        self.RDENS = np.array([self.scalars[f"RDENS{i}"] for i in (1, 2, 3)])

    def _parse_particles(self):
        def read(id_str, name):
            return self.group[f"{id_str} {name}"][:]

        nstars = int(self.scalars["N_SINGLE"])

        coords = np.stack(
            [read("001", "X1"), read("002", "X2"), read("003", "X3")], axis=1
        )
        vels = np.stack(
            [read("004", "V1"), read("005", "V2"), read("006", "V3")], axis=1
        )

        M = read("023", "M")
        Names = read("032", "Name")
        ptype = read("033", "Type")
        ASPN = read("035", "ASPN")

        try:
            # read stellar data
            Rstar = read("026", "R*")
            Lstar = read("027", "L*")
            Teff = read("028", "Teff*")
            Rcore = read("029", "RC*")
            Mcore = read("030", "MC*")
            kw = read("031", "KW")
            self._hr_empty = False
        except:
            print("Found no stellar evolution data. To enable HR output, adjust KZ(12)")
            self._hr_empty = True

        # This part of code is needed for indexing from 1
        size = nstars + 1
        self.X = np.zeros((size, 3))
        self.V = np.zeros((size, 3))
        self.Mass = np.zeros(size)
        self.Name = np.zeros(size, dtype=int)
        self.type = np.zeros(size, dtype=int)
        self.ASPN = np.zeros(size)

        if not self._hr_empty:
            self.Radius = np.zeros(size)
            self.Lum = np.zeros(size)
            self.Teff = np.zeros(size)
            self.Rcore = np.zeros(size)
            self.Mcore = np.zeros(size)
            self.kw = np.zeros(size)

        self.X[1:] = coords - self.RDENS
        self.V[1:] = vels
        self.Mass[1:] = M
        self.Name[1:] = Names
        self.type[1:] = ptype
        self.ASPN[1:] = ASPN

        if not self._hr_empty:
            self.Radius[1:] = Rstar
            self.Lum[1:] = Lstar
            self.Teff[1:] = Teff
            self.Rcore[1:] = Rcore
            self.Mcore[1:] = Mcore
            self.kw[1:] = kw

        # derived
        self.RR = np.linalg.norm(self.X, axis=1)
        self.VV = np.linalg.norm(self.V, axis=1)
        self.LZ_spec = np.sqrt(self.X[:, 0] ** 2 + self.X[:, 1] ** 2) * np.sqrt(
            self.V[:, 0] ** 2 + self.V[:, 1] ** 2
        )
        self.LZ = self.Mass * self.LZ_spec

    def to_dict(self):
        """Return snapshot data as dict of arrays."""
        data = {
            "scalars": self.scalars,
            "X": self.X,
            "V": self.V,
            "Mass": self.Mass,
            "Radius": self.Radius,
            "Lum": self.Lum,
            "Teff": self.Teff,
            "Name": self.Name,
            "type": self.type,
            "ASPN": self.ASPN,
            "RR": self.RR,
            "VV": self.VV,
            "LZ": self.LZ,
        }
        return data

    def close(self):
        self._f.close()


if __name__ == "__main__":
    snap = NBodySnapshot("test_2705_hdf5/snap.40_5.h5part")
    print(f"Loaded: N={snap.scalars['N']}, NPAIRS={snap.scalars['NPAIRS']}")
    print(snap.X.shape, snap.X[0])
    snap.close()
