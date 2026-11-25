# Data sources

Every raw file in `data/raw/` comes from the **UCI Machine Learning Repository**, carries a DOI and the **CC BY 4.0** licence, and its byte size matches the UCI file manifest exactly. SHA-256 hashes are listed in §3 so anyone can verify a clone.

The project reproduces *Wang, Du, Zhang & Shi (2022), "Ranking Features to Promote Diversity: An Approach Based on Sparse Distance Correlation"* (Technometrics 64(3)), whose data setting is

> **n products × p process features → 1 quality variable**, with large p, few root causes, and strongly redundant features.

**What was verified and what was not** — so citations do not silently overreach:

| Item | Status |
|---|---|
| Dataset title, creators, DOI, licence, donation date, #instances / #features | ✅ scraped from each UCI dataset page (`DOI`, `Creators`, `DateDonated`, `License`, `# Instances`) |
| File names and byte sizes | ✅ compared byte-for-byte with the UCI `filesInfo` manifest — all match |
| SHA-256 of committed files | ✅ computed locally |
| "Published in <journal>, <year>, Volume <n>" | ✅ taken from the UCI page text |
| Article **volume/issue/pages/DOI** of those journal papers | ❌ **not verified** (Crossref rate-limited this session) — look them up on the journal site |
| Tianchi mirror entries | ⚠️ only title + page existence checked; not downloaded, fields not inspected |

---

## 1. Overview

| # | Dataset (exact UCI title) | UCI ID | Creators | DOI | Donated | Licence | Instances / features | Committed |
|---|---|---|---|---|---|---|---|---|
| 1 | **SECOM** | [179](https://archive.ics.uci.edu/dataset/179/secom) | Michael McCann, Adrian Johnston | [10.24432/C54305](https://doi.org/10.24432/C54305) | 2008-11-18 | CC BY 4.0 | 1567 / 591 | ✅ full |
| 2 | **Condition monitoring of hydraulic systems** | [447](https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems) | Nikolai Helwig, Eliseo Pignanelli, Andreas Schütze | [10.24432/C5CW21](https://doi.org/10.24432/C5CW21) | 2018-04-25 | CC BY 4.0 | 2205 cycles / 17 sensors | ⚠️ `profile.txt` + 85-feature cache; 530 MB curves via `download_data.py --include-hydraulic-raw` |
| 3 | **Gas Sensor Array Drift Dataset** | [224](https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset+at+different+concentrations) | Alexander Vergara | [10.24432/C5RP6W](https://doi.org/10.24432/C5RP6W) | 2012-04-24 | CC BY 4.0 | 13910 / 128 | ✅ full (10 batches) |
| 4 | **Steel Plates Faults** | [198](https://archive.ics.uci.edu/dataset/198/steel+plates+faults) | M Buscema, S Terzi, W Tastle | [10.24432/C5J88N](https://doi.org/10.24432/C5J88N) | 2010-10-25 | CC BY 4.0 | 1941 / 27 | ✅ full |
| 5 | **Wine Quality** | [186](https://archive.ics.uci.edu/dataset/186/wine+quality) | Paulo Cortez, A. Cerdeira, F. Almeida, T. Matos, J. Reis | [10.24432/C56S3T](https://doi.org/10.24432/C56S3T) | 2009-10-06 | CC BY 4.0 | 1599 red / 4898 white | ✅ full |
| 6 | **Appliances Energy Prediction** | [374](https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction) | Luis Candanedo | [10.24432/C5VC8G](https://doi.org/10.24432/C5VC8G) | 2017-02-14 | CC BY 4.0 | 19735 / 28 | ✅ full |

---

## 2. Copy-paste citations

### ① SECOM
> McCann, M., & Johnston, A. (2008). *SECOM* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C54305

- Page: https://archive.ics.uci.edu/dataset/179/secom
- Zip used: `https://archive.ics.uci.edu/static/public/179/secom.zip`
- Files: `data/raw/secom/secom.data` (5,389,983 B), `secom_labels.data` (40,638 B), `secom.names` (4,223 B)

### ② Condition monitoring of hydraulic systems
> Helwig, N., Pignanelli, E., & Schütze, A. (2018). *Condition monitoring of hydraulic systems* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CW21

- Page: https://archive.ics.uci.edu/dataset/447/condition+monitoring+of+hydraulic+systems
- Zip used: `https://archive.ics.uci.edu/static/public/447/condition+monitoring+of+hydraulic+systems.zip`
- Committed: `profile.txt` (targets), `description.txt`, `hydraulic_features.npz` (17 sensors × 5 statistics = 85 columns)
- Not committed: `PS1–PS6, EPS1, FS1, FS2, TS1–TS4, VS1, CE, CP, SE` (530 MB) — regenerate with the download script

### ③ Gas Sensor Array Drift Dataset
> Vergara, A. (2012). *Gas Sensor Array Drift Dataset* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5RP6W

- Page: https://archive.ics.uci.edu/dataset/224/gas+sensor+array+drift+dataset+at+different+concentrations
- Zip used: `https://archive.ics.uci.edu/static/public/224/gas+sensor+array+drift+dataset.zip`
- Files: `data/raw/gas_drift/batch1.dat … batch10.dat` (libsvm format: `label idx:value …`)
- Tianchi mirror: https://tianchi.aliyun.com/dataset/144721 (Gas Sensor Array Under Dynamic Gas Mixtures)

### ④ Steel Plates Faults
> Buscema, M., Terzi, S., & Tastle, W. (2010). *Steel Plates Faults* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5J88N

- Page: https://archive.ics.uci.edu/dataset/198/steel+plates+faults
- Zip used: `https://archive.ics.uci.edu/static/public/198/steel+plates+faults.zip`
- Files: `Faults.NNA` (299,482 B; 27 features + 7 one-hot labels), `Faults27x7_var` (497 B)

### ⑤ Wine Quality
> Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). *Modeling wine preferences by data mining from physicochemical properties.* **Decision Support Systems**.
>
> Dataset: Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). *Wine Quality* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C56S3T

- The "Decision Support Systems, 2009" line is what the UCI page states (original text: *By P. Cortez, A. Cerdeira, Fernando Almeida, Telmo Matos, J. Reis. 2009 Published in Decision Support Systems*). **Volume/issue/pages were not verified** — look them up on the journal site, or cite the dataset DOI above.
- Page: https://archive.ics.uci.edu/dataset/186/wine+quality
- Zip used: `https://archive.ics.uci.edu/static/public/186/wine+quality.zip`
- Files: `winequality-red.csv` (84,199 B, 1599 rows), `winequality-white.csv` (264,426 B, 4898 rows), `winequality.names`

### ⑥ Appliances Energy Prediction
> Candanedo, L., Feldheim, V., & Deramaix, D. (2017). *Data driven prediction models of energy use of appliances in a low-energy house.* **Energy and Buildings, 140**.
>
> Dataset: Candanedo, L. (2017). *Appliances Energy Prediction* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5VC8G

- "Energy and Buildings, Volume 140, 2017" is also from the UCI page; **pages and article DOI were not verified**.
- Page: https://archive.ics.uci.edu/dataset/374/appliances+energy+prediction
- Zip used: `https://archive.ics.uci.edu/static/public/374/appliances+energy+prediction.zip`
- Files: `energydata_complete.csv` (11,979,363 B, 19735 rows × 29 columns)

---

## 3. Checksums (verify a clone)

| File (relative to `data/raw/`) | Bytes | SHA-256 |
|---|---|---|
| `secom/secom.data` | 5,389,983 | `20f0e7ee434f7dcbae0eea9ffff009a2b57f42d6b0dc9a5bd4f00782c0a3374c` |
| `secom/secom_labels.data` | 40,638 | `126884cf453705c9e61a903fe906f0665a3b45ce3639e621edc5c93c89627e03` |
| `steel_plates/Faults.NNA` | 299,482 | `08994f5b0185a8e6cc22afe9910fd36834990fb1ca30852ed79012a832fbff55` |
| `steel_plates/Faults27x7_var` | 497 | `887dbfa140b48877b706865ef277550dc0203699243c600e24bfe8b090a9a953` |
| `wine_quality/winequality-red.csv` | 84,199 | `4a402cf041b025d4566d954c3b9ba8635a3a8a01e039005d97d6a710278cf05e` |
| `wine_quality/winequality-white.csv` | 264,426 | `76c3f809815c17c07212622f776311faeb31e87610d52c26d87d6e361b169836` |
| `appliances/energydata_complete.csv` | 11,979,363 | `2820bf712ad0275cb18b85a05250926100d8e65ebb9f4d2d016ca91ea152a25d` |
| `hydraulic/profile.txt` | 31,196 | `867987ca884b2f0fd607ad3918329eba887d095af2befa21122cea518eaa584a` |
| `hydraulic/FS1.txt` *(not committed)* | 7,581,926 | `7ff09b17047f776befc136b7902bc7bd4419f96dc107a7ae94d8c412effe0375` |
| `gas_drift/batch1.dat` | 752,726 | `f346beee8e0c5e31ac5961845b6d96a70dc1ccf799481592fb2f0d96a81952e6` |

PowerShell: `Get-FileHash data\raw\secom\secom.data -Algorithm SHA256`
Or run `python scripts/download_data.py --verify-only`.

---

## 4. Licence

All six datasets are **CC BY 4.0** — the UCI pages say, verbatim: *"This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license."*

Attribution: keep the creator names and DOIs from §1/§2 in any report, notebook header, or derived table.

---

## 5. Tianchi entries (NOT used for the committed files)

Tianchi requires an Aliyun login (some datasets also need points) and its pages are client-rendered, so the archives cannot be fetched programmatically here. These entries were only checked for title + page existence:

| Tianchi entry | Relation to this repo |
|---|---|
| https://tianchi.aliyun.com/dataset/144721 | Same family as ③ (gas sensors), usable as extra data |
| https://tianchi.aliyun.com/dataset/71871 | Fan radial-vibration spectra; spectrum amplitudes as features, fault type as y |
| https://tianchi.aliyun.com/dataset/146416 | MVTec-AD industrial defect **images** — needs feature extraction first |
| https://tianchi.aliyun.com/dataset/77328 | Mixed-pattern wafer-map defects, **images** — CNN territory, not SpaDC's tabular setting |
| https://tianchi.aliyun.com/dataset/158636 | 2023 iFlytek battery data, fields unverified |
