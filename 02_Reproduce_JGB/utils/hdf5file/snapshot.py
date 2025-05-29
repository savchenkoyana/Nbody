"""Load and access Nbody6++GPU HDF5 snapshot data."""

import warnings

import h5py
import numpy as np

from .mapping import _SCALAR_MAP
from .mapping import _SINGLE_PARTICLE_HR_MAP
from .mapping import _SINGLE_PARTICLE_MAP


class NBodySnapshot:
    """Convenience class to load and access Nbody6++GPU HDF5 snapshot data.

    Parses scalar parameters and particle data (singles and binaries).
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self._load_file()
        self._parse_scalars()
        self._parse_particles()

    def _load_file(self):
        self._f = h5py.File(self.filepath, "r")
        self.step = next(iter(self._f.keys()))
        self.group = self._f[self.step]

    def _read(self, id_str, name):
        return self.group[f"{id_str} {name}"][:]

    def _load_basic(self):
        for code, label in _SINGLE_PARTICLE_MAP.items():
            setattr(self, label, self._read(code, label))

    def _load_hr(self):
        for code, label in _SINGLE_PARTICLE_HR_MAP.items():
            setattr(self, label, self._read(code, label))

    def _parse_scalars(self):
        S = self.group["000 Scalars"][:]

        self.scalars = {name: S[idx] for idx, name in _SCALAR_MAP.items()}
        self.TTOT = self.scalars["TTOT"]
        self.NPAIRS = int(self.scalars["NPAIRS"])
        self.N = int(self.scalars["N"])
        self.RDENS = np.array([self.scalars[f"RDENS{i}"] for i in (1, 2, 3)])

    def _parse_particles(self):
        self._load_basic()
        try:
            self._load_hr()
            self._hr_empty = False
        except:
            warnings.warn(
                "Found no stellar evolution data. To enable HR output, adjust KZ(12)"
            )
            self._hr_empty = True

        self.X = np.stack([self.X1, self.X2, self.X3], axis=1) - self.RDENS
        self.V = np.stack([self.V1, self.V2, self.V3], axis=1)

        # derived
        self.RR = np.linalg.norm(self.X, axis=1)
        self.VV = np.linalg.norm(self.V, axis=1)
        self.LZ_spec = np.sqrt(self.X[:, 0] ** 2 + self.X[:, 1] ** 2) * np.sqrt(
            self.V[:, 0] ** 2 + self.V[:, 1] ** 2
        )
        self.LZ = self.M * self.LZ_spec

    def close(self):
        self._f.close()
