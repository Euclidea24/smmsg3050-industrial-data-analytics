"""Unified loaders for the six industrial datasets in `data/raw/`.

Each loader returns ``(X, y, meta)`` with

* ``X``    : ndarray ``(n, p)`` process features (float, missing values imputed)
* ``y``    : ndarray ``(n,)``  quality variable (binary / ordinal / class / float)
* ``meta`` : dict with the provenance (source URL, DOI, license, citation)

Run this file directly to check every dataset can be read::

    python scripts/load_spadc_data.py

Provenance for every file is documented in ``docs/data-sources.md``.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "data", "raw")


# --------------------------------------------------------------------- helpers
def _impute_median(X):
    """Column-wise median imputation (SECOM has ~4.5% missing)."""
    X = np.array(X, dtype=float)
    med = np.nanmedian(X, axis=0)
    idx = np.where(np.isnan(X))
    X[idx] = np.take(med, idx[1])
    return X


def _drop_constant(X):
    """Constant columns carry no ranking information."""
    keep = X.std(axis=0) > 1e-12
    return X[:, keep]


def _stats_block(a):
    """Compress one (n_cycles, n_samples) sensor recording into 5 features."""
    a = np.asarray(a, dtype=float)
    mean = a.mean(1)
    idx = np.arange(a.shape[1], dtype=float)
    idx -= idx.mean()
    slope = (a - mean[:, None]) @ idx / (idx ** 2).sum()
    return np.column_stack([mean, a.std(1), a.min(1), a.max(1), slope])


# --------------------------------------------------------------------- SECOM
def load_secom():
    """SECOM, semiconductor manufacturing.  n=1567, p=474 (590 raw, constants dropped).

    y = 1 means the wafer **failed** (raw label -1); y = 0 means pass.
    """
    raw = os.path.join(RAW, "secom", "secom.data")
    rows = [ln.split() for ln in open(raw, encoding="utf-8", errors="ignore") if ln.strip()]
    X = np.array([[np.nan if v == "?" else float(v) for v in r] for r in rows])
    X = _drop_constant(_impute_median(X))
    lab = pd.read_csv(os.path.join(RAW, "secom", "secom_labels.data"),
                      sep=r"\s+", header=None, engine="python")
    y = (lab.iloc[:, 0].values == -1).astype(int)
    meta = {
        "name": "SECOM",
        "n": X.shape[0], "p": X.shape[1],
        "target": "wafer pass / fail", "fail_rate": round(float(y.mean()), 4),
        "source": "UCI 179",
        "doi": "10.24432/C54305",
        "license": "CC BY 4.0",
        "citation": ("McCann, M., & Johnston, A. (2008). SECOM [Dataset]. "
                     "UCI Machine Learning Repository. https://doi.org/10.24432/C54305"),
    }
    return X, y, meta


# ----------------------------------------------------------------- hydraulic
def load_hydraulic(which=0):
    """Condition monitoring of hydraulic systems.  n=2205 cycles, p=85.

    ``which`` chooses the quality variable:

    ==== ============================ ==============================
    0    cooler condition             3 / 20 / 100
    1    valve condition              73 / 80 / 90 / 100
    2    pump leakage                 0 / 1 / 2
    3    accumulator pressure         90 / 100 / 115 / 130
    4    stability flag               0 / 1
    ==== ============================ ==============================

    The 17 per-cycle sensor curves (530 MB) are **not** committed. Use
    ``data/raw/hydraulic/hydraulic_features.npz`` (85 features, 0.6 MB) or run
    ``scripts/download_data.py --include-hydraulic-raw`` to fetch the curves.
    """
    base = os.path.join(RAW, "hydraulic")
    prof = pd.read_csv(os.path.join(base, "profile.txt"), sep=r"\s+", header=None).values
    targets = ["cooler condition", "valve condition", "pump leakage",
               "accumulator pressure", "stability flag"]
    cache = os.path.join(base, "hydraulic_features.npz")
    if os.path.exists(cache) and which == 0:
        X = np.load(cache)["X"]
    else:
        sens = ["PS1", "PS2", "PS3", "PS4", "PS5", "PS6", "EPS1", "FS1", "FS2",
                "TS1", "TS2", "TS3", "TS4", "VS1", "CE", "CP", "SE"]
        blocks = []
        for s in sens:
            a = pd.read_csv(os.path.join(base, s + ".txt"), sep=r"\s+", header=None).values
            blocks.append(_stats_block(a))
        X = np.hstack(blocks)
    y = prof[:, which].astype(int)
    meta = {
        "name": "Condition monitoring of hydraulic systems",
        "n": X.shape[0], "p": X.shape[1],
        "target": targets[which], "targets": targets,
        "source": "UCI 447",
        "doi": "10.24432/C5CW21",
        "license": "CC BY 4.0",
        "citation": ("Helwig, N., Pignanelli, E., & Schütze, A. (2018). Condition monitoring "
                     "of hydraulic systems [Dataset]. UCI Machine Learning Repository. "
                     "https://doi.org/10.24432/C5CW21"),
    }
    return X, y, meta


# ---------------------------------------------------------------- steel plates
def load_steel():
    """Steel Plates Faults.  n=1941, p=27.

    The seven label columns are one-hot (exactly one 1 per row), so summing them
    would give a constant. ``y`` is therefore the fault **type** (0-6).
    """
    a = pd.read_csv(os.path.join(RAW, "steel_plates", "Faults.NNA"),
                    sep=r"\s+", header=None).values
    X = a[:, :27].astype(float)
    y = a[:, 27:].astype(int).argmax(1)
    meta = {
        "name": "Steel Plates Faults",
        "n": X.shape[0], "p": X.shape[1],
        "target": "defect type (7 classes)",
        "source": "UCI 198",
        "doi": "10.24432/C5J88N",
        "license": "CC BY 4.0",
        "citation": ("Buscema, M., Terzi, S., & Tastle, W. (2010). Steel Plates Faults "
                     "[Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5J88N"),
    }
    return X, y, meta


# ------------------------------------------------------------------- wine
def load_wine(color="red"):
    """Wine Quality (physicochemical tests -> sensory score 3-9)."""
    a = pd.read_csv(os.path.join(RAW, "wine_quality", "winequality-%s.csv" % color), sep=";")
    X = a.iloc[:, :-1].values.astype(float)
    y = a.iloc[:, -1].values.astype(int)
    meta = {
        "name": "Wine Quality (%s)" % color,
        "n": X.shape[0], "p": X.shape[1],
        "target": "quality score (3-9)",
        "source": "UCI 186",
        "doi": "10.24432/C56S3T",
        "license": "CC BY 4.0",
        "citation": ("Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). "
                     "Modeling wine preferences by data mining from physicochemical properties. "
                     "Decision Support Systems. Dataset: https://doi.org/10.24432/C56S3T"),
    }
    return X, y, meta


# --------------------------------------------------------------- appliances
def load_appliances():
    """Appliances Energy Prediction: indoor sensors -> appliance energy use (Wh)."""
    a = pd.read_csv(os.path.join(RAW, "appliances", "energydata_complete.csv"))
    drop = [c for c in a.columns if c.lower() in ("date", "appliances")]
    X = a.drop(columns=drop).values.astype(float)
    y = a["Appliances"].values.astype(float)
    meta = {
        "name": "Appliances Energy Prediction",
        "n": X.shape[0], "p": X.shape[1],
        "target": "Appliances (Wh)",
        "source": "UCI 374",
        "doi": "10.24432/C5VC8G",
        "license": "CC BY 4.0",
        "citation": ("Candanedo, L., Feldheim, V., & Deramaix, D. (2017). Data driven prediction "
                     "models of energy use of appliances in a low-energy house. Energy and "
                     "Buildings, 140. Dataset: https://doi.org/10.24432/C5VC8G"),
    }
    return X, y, meta


# --------------------------------------------------------------- gas sensors
def _read_gas_file(path):
    """UCI gas files are libsvm-like: ``label  idx:value idx:value ...``."""
    rows, labels = [], []
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for ln in fh:
            parts = ln.split()
            if not parts:
                continue
            labels.append(float(parts[0]))
            n_idx = max(int(t.split(":")[0]) for t in parts[1:])
            row = np.zeros(n_idx)
            for t in parts[1:]:
                k, v = t.split(":")
                row[int(k) - 1] = float(v)
            rows.append(row)
    return np.array(rows, dtype=float), np.array(labels)


def load_gas(batch=None):
    """Gas Sensor Array Drift (16 sensors x 8 features = 128)."""
    base = os.path.join(RAW, "gas_drift")
    files = sorted(f for f in os.listdir(base) if f.endswith(".dat"))
    if batch is not None:
        files = [files[batch]]
    Xs, ys = [], []
    for f in files:
        Xb, yb = _read_gas_file(os.path.join(base, f))
        Xs.append(Xb)
        ys.append(yb)
    X = np.vstack(Xs)
    _, y = np.unique(np.concatenate(ys), return_inverse=True)
    meta = {
        "name": "Gas Sensor Array Drift Dataset",
        "n": X.shape[0], "p": X.shape[1],
        "target": "gas class", "batches": len(files),
        "source": "UCI 224",
        "doi": "10.24432/C5RP6W",
        "license": "CC BY 4.0",
        "citation": ("Vergara, A. (2012). Gas Sensor Array Drift Dataset [Dataset]. "
                     "UCI Machine Learning Repository. https://doi.org/10.24432/C5RP6W"),
    }
    return X, y, meta


LOADERS = {
    "secom": load_secom,
    "hydraulic": load_hydraulic,
    "steel": load_steel,
    "wine_red": lambda: load_wine("red"),
    "wine_white": lambda: load_wine("white"),
    "appliances": load_appliances,
    "gas": load_gas,
}


def load(name="secom"):
    """Unified entry point: ``load("secom") -> (X, y, meta)``."""
    if name not in LOADERS:
        raise KeyError("unknown dataset %r; choose from %s" % (name, sorted(LOADERS)))
    return LOADERS[name]()


if __name__ == "__main__":
    for key in LOADERS:
        try:
            X, y, m = load(key)
            print("%-11s n=%5d  p=%4d  y=%s" % (key, X.shape[0], X.shape[1], m["target"]))
        except Exception as exc:  # noqa: BLE001
            print("%-11s FAILED: %s" % (key, exc))
