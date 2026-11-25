# Data

Raw data may be committed; derived data is not. This directory documents what the data is, where it came from, and how to obtain it.

## Dataset card

Six industrial datasets back the SpaDC study (*Wang, Du, Zhang & Shi, 2022*). The setting they share: **n products × p process features → one quality variable**, with large p, few root causes, and strongly redundant features.

| Dataset | UCI | n | p | Quality variable y | Committed | File |
|---|---|---|---|---|---|---|
| SECOM (semiconductor) | [179](https://archive.ics.uci.edu/dataset/179/secom) | 1567 | 474 (590 raw) | wafer pass / fail | ✅ | `raw/secom/` |
| Hydraulic condition monitoring | [447](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems) | 2205 | 85 | cooler / valve / pump / accumulator / stability | ⚠️ targets + feature cache | `raw/hydraulic/` |
| Gas sensor array drift | [224](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset+at+different+concentrations) | 13910 | 128 | gas class (6) | ✅ | `raw/gas_drift/` |
| Steel plates faults | [198](https://archive.ics.uci.edu/dataset/198/steel+plates+faults) | 1941 | 27 | defect type (7) | ✅ | `raw/steel_plates/` |
| Wine quality | [186](https://archive.ics.uci.edu/dataset/186/wine+quality) | 1599 / 4898 | 11 | sensory score 3–9 | ✅ | `raw/wine_quality/` |
| Appliances energy | [374](https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction) | 19735 | 27 | appliance energy load (Wh) | ✅ | `raw/appliances/` |

| Field | Value |
|---|---|
| Source | UCI Machine Learning Repository (per-dataset DOIs in [`docs/data-sources.md`](../docs/data-sources.md)) |
| Licence | **CC BY 4.0** for all six |
| Retrieval date | 2026-11-25 |
| Version / checksum | SHA-256 per file, see `docs/data-sources.md` §3; verify with `python scripts/download_data.py --verify-only` |
| Unit of analysis | one row = one product / wafer / cycle / bottle / timestamp |
| Known issues | SECOM has ~4.5% missing values (median-imputed in the loader) and 116 constant columns; the steel label columns are one-hot, so summing them yields a constant — use `argmax`; the gas files are libsvm-formatted, not CSV |

## Placement

```text
data/raw/        original files (may be committed; one copy only)
data/interim/    intermediate cleaned data (not committed)
data/processed/  model-ready data (not committed)
```

```text
data/raw/
├── secom/          secom.data, secom_labels.data, secom.names
├── hydraulic/      profile.txt, description.txt, hydraulic_features.npz
├── gas_drift/      batch1.dat … batch10.dat
├── steel_plates/   Faults.NNA, Faults27x7_var
├── wine_quality/   winequality-red.csv, winequality-white.csv, winequality.names
└── appliances/     energydata_complete.csv
```

## Acquisition

```bash
# what is already in the repo: verify it
python scripts/download_data.py --verify-only

# re-download the small datasets (~40 MB) from UCI
python scripts/download_data.py

# also fetch the 17 per-cycle hydraulic sensor curves (530 MB, not committed)
python scripts/download_data.py --include-hydraulic-raw
```

Everything is fetched over plain HTTPS from `archive.ics.uci.edu/static/public/...`; no login, no token. Sizes and hashes are checked after download.

**Why the hydraulic curves are not committed:** `PS1–PS6` and `EPS1` are 47–91 MB each (530 MB total), above GitHub's practical per-file limit. `hydraulic_features.npz` (0.6 MB) holds the 17 sensors × 5 statistics = 85 features that the loader uses, so a fresh clone runs without the curves.

## Rules

- Raw data may be committed under `data/raw/`; commit one copy only (archive or extracted files, not both).
- Never commit credentials, personal information, or per-row predictions.
- Record the license, retrieval date, checksum, and attribution before using the data.
- Keep `data/raw/` read-only; write cleaned outputs to `data/interim/` or `data/processed/`.
- GitHub rejects files over 100 MiB and warns above 50 MiB; use Git LFS or an external location for those.
