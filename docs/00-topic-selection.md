# 00 · Topic and Dataset Selection

**Status:** decided (dataset choice frozen; open issues below)
**Owner:** TBD
**Decision deadline:** 2026-11-26
**Linked from:** `README.md` § Topic and dataset selection

## Course constraints

- The topic must be related to industrial data analytics.
- A public dataset (Kaggle, Tianchi, or another public source) or a self-defined industrial problem is acceptable.
- The topic must support the full rubric: problem statement, preprocessing, modeling, model selection, evaluation, and interpretation.

## Rubric → what a dataset must afford

| Rubric item | Points | Requirement this places on the data |
|---|---|---|
| Accuracy | 20 | Unambiguous target, no leakage, metric matched to the task (accuracy is meaningless on imbalanced data) |
| Problem statement | 6 | A real decision-maker and a cost of being wrong |
| Data preprocessing | 4 | Something to clean: missing values, scales, categoricals, imbalance, time order |
| Modeling | 6 | Enough rows to fit, p/n sane, at least 2–3 plausible model families |
| Model selection | 3 | Models that actually differ; hyper-parameters worth tuning |
| Evaluation | 6 | A clean hold-out scheme (time / batch / group) and interpretable metrics |
| Interpret results | 5 | Features with physical meaning → importance, rules, cluster profiles |
| Relevance | 20 | Visible use of course methods: preprocessing, association rules, CART, Naive Bayes, ROC/TPR/FPR, CV + Welch t-test, clustering, feature ranking |
| Writing / Presentation | 30 | Results must fit into 2–3 hero figures |

## Scoring model

Ten dimensions, 1–5 each (5 = strong). Two weightings were compared; **v2 (presentation-forward) is the one used**.

| Dimension | v1 (relevance-first) | **v2 (used)** | What it measures |
|---|---|---|---|
| D1 Industrial relevance | 20% | 12% | Is it a real process/asset/product, with a decision behind it |
| D2 Course-method fit | 20% | 15% | Can it exercise preprocessing, CART, NB, ROC, CV, clustering |
| D3 Preprocessing space | 15% | 10% | Missing, scales, categoricals, imbalance, time order |
| D4 Modeling feasibility | 15% | 10% | n, p/n, class count, one-day baseline |
| D5 Evaluation feasibility | 15% | 10% | Clean hold-out, meaningful metrics |
| D6 Interpretability | 10% | 5% | Physical meaning of features |
| D7 Risk / cost (5 = low risk) | 5% | 3% | Leakage, imbalance trap, compute, label semantics |
| **P1 Figure potential** | — | **15%** | Can it produce one-glance figures |
| **P2 Story strength** | — | **12%** | One-sentence narrative, dramatic hook |
| **P3 Visual variety** | — | **8%** | Curves / scatter / confusion matrix / images at once |
| Total | 100% | **100%** | Presentation-related weight: **35%** |

Weighted score = Σ (score × weight). Example: Hydraulic = 5(.12) + 4(.15) + 4(.10) + 4(.10) + 4(.10) + 5(.05) + 4(.03) + 5(.15) + 5(.12) + 5(.08) = **4.52**.

## Candidates (everything currently in `data/raw/`, checked 2026-11-25)

`ext` = extracted and loadable via `scripts/load_spadc_data.py`; `zip` = archive only, no loader yet.

| # | Dataset (UCI id) | Raw state | D1 | D2 | D3 | D4 | D5 | D6 | D7 | P1 | P2 | P3 | **v2 score** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Hydraulic condition monitoring (447) | ext | 5 | 4 | 4 | 4 | 4 | 5 | 4 | 5 | 5 | 5 | **4.52** |
| 2 | AI4I 2020 predictive maintenance (601) | zip | 4 | 4 | 4 | 5 | 4 | 4 | 3 | 5 | 5 | 5 | **4.42** |
| 3 | Gas sensor array drift (224) | ext | 4 | 4 | 5 | 4 | 5 | 3 | 3 | 5 | 4 | 4 | **4.27** |
| 4 | Steel industry energy consumption (851) | zip | 5 | 4 | 4 | 4 | 3 | 4 | 4 | 5 | 4 | 5 | **4.25** |
| 5 | SECOM semiconductor (179) | ext | 5 | 5 | 5 | 3 | 4 | 5 | 3 | 4 | 4 | 3 | **4.21** |
| 6 | Combined cycle power plant (294) | zip | 5 | 4 | 3 | 5 | 4 | 4 | 5 | 4 | 4 | 4 | **4.15** |
| 7 | Garment worker productivity (597) | zip | 4 | 4 | 5 | 5 | 3 | 4 | 3 | 4 | 4 | 4 | **4.07** |
| 8 | Concrete compressive strength (165) | zip | 3 | 5 | 3 | 5 | 4 | 4 | 5 | 4 | 3 | 4 | **3.94** |
| 9 | Appliances energy prediction (374) | ext | 3 | 4 | 5 | 5 | 3 | 3 | 3 | 5 | 3 | 4 | **3.93** |
| 10 | Steel plates faults (198) | ext | 4 | 5 | 3 | 5 | 4 | 4 | 5 | 3 | 3 | 3 | **3.83** |
| 11 | Dry bean (602) | zip | 2 | 4 | 3 | 5 | 4 | 4 | 5 | 5 | 3 | 4 | **3.82** |
| 12 | Seoul bike sharing (560) | zip | 2 | 4 | 4 | 5 | 3 | 3 | 4 | 5 | 3 | 4 | **3.74** |
| 13 | Electrical grid stability (471) | zip | 3 | 4 | 3 | 5 | 4 | 3 | 4 | 4 | 3 | 4 | **3.71** |
| 14 | Sensorless drive diagnosis (325) | zip | 4 | 4 | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 4 | **3.70** |
| 15 | Wholesale customers (292) | zip | 2 | 4 | 4 | 5 | 3 | 4 | 5 | 4 | 3 | 4 | **3.67** |
| 16 | Tetouan city power (849) | zip | 3 | 4 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 4 | **3.61** |
| 17 | Airfoil self-noise (291) | zip | 3 | 4 | 2 | 5 | 4 | 4 | 5 | 3 | 3 | 3 | **3.46** |
| 18 | Wine quality (186) | ext | 2 | 3 | 2 | 5 | 3 | 3 | 5 | 3 | 2 | 2 | **2.84** |

Not scored: three archives duplicate already-extracted datasets (`179-secom.zip`, `186-wine+quality.zip`, `198-steel+plates+faults.zip`) — see Open issues. Datasets discussed earlier but **not in the repo** (NASA C-MAPSS, WM-811K, Bosch, NEU surface defects) are excluded: nothing local to verify, and Kaggle needs a login.

## Ranking (computed)

| Rank | Dataset | v2 | Rank under v1 (no presentation weight) |
|---|---|---|---|
| 1 | Hydraulic | 4.52 | 2 (4.30) |
| 2 | AI4I 2020 | 4.42 | 4 (4.12) |
| 3 | Gas drift | 4.27 | 5 (4.15) |
| 4 | Steel industry energy | 4.25 | — |
| 5 | SECOM | 4.21 | **1 (4.45)** |

**Sensitivity:** raising the presentation weight to 35% moves **SECOM from 1st to 5th** and **Hydraulic from 2nd to 1st**, and pulls AI4I into the top three. The two rankings agree that Hydraulic is top-two; they disagree on whether depth (SECOM) or showmanship (AI4I, Gas) matters more.

## Decision

- **Chosen (primary): Hydraulic condition monitoring (447).**
  - Four independent targets (cooler / valve / pump / accumulator + stability) → one dataset yields a multi-task story.
  - 17 physical sensor channels → raw curves are presentable and interpretable; 2205 cycles is enough for a clean split.
  - Runnable today: `load("hydraulic")`, 85 engineered features, checksums pinned.
- **Chosen (secondary): AI4I 2020 predictive maintenance (601).**
  - The canonical "predict failure before it happens" narrative; 10 000 rows × 6 features runs in seconds.
  - **Trap to document:** `Machine failure` and the five mode flags (TWF/HDF/PWF/OSF/RNF) are derived from the process variables by published rules — including them leaks the label. Drop them, keep the five sensors.
  - Still zip-only: needs extraction + a loader before it is runnable.
- **Chosen (tertiary / generalisation): Gas sensor array drift (224).**
  - One figure (PCA coloured by batch) explains "the model that worked yesterday fails today".
  - Adds an evaluation design the other two lack: **leave-one-batch-out** vs random split.
- **Why not the runner-up (Steel industry energy, 851):** best pure visual (35 041 rows of plant load curves) but it is a **time-series regression** with heavy autocorrelation; a random split leaks, and a correct temporal split leaves little data for model comparison. Kept as the alternate if Hydraulic's multi-target split proves messy.
- **Why not the v1 winner (SECOM):** still the deepest dataset (474 features, 4.5% missing, 6.6% positive class) — but its figures are ROC/PR curves and importance bars, hard to make legible in 11 minutes. Keep it as the "depth" option if the group has a strong visualiser.
- **Fallback if access or effort fails:** #6 Combined cycle power plant (4.15) — 9568 rows, 4 features, no missing values, one-day baseline guaranteed.
- **Dataset card:** `data/README.md`
- **Decided by / date:** analysis 2026-11-25, recorded in this commit

## Verification status of the chosen three

| Dataset | Files in repo | Extracted | Loader | SHA-256 pinned |
|---|---|---|---|---|
| Hydraulic | `profile.txt`, `description.txt`, `hydraulic_features.npz` (530 MB raw curves **not** committed) | ✅ | ✅ | ✅ |
| AI4I 2020 | `data/raw/601-ai4i+2020+predictive+maintenance+dataset/*.zip` | ❌ | ❌ | ❌ |
| Gas drift | `batch1.dat … batch10.dat` | ✅ | ✅ | ✅ |

## Open issues

1. **AI4I is zip-only.** Extract it, add `load_ai4i()`, pin its checksum in `docs/data-sources.md`. Until then the #2 choice is a paper decision, not a runnable one.
2. **Duplicate copies.** `179-secom.zip`, `186-wine+quality.zip`, `198-steel+plates+faults.zip` duplicate the extracted `secom/`, `wine_quality/`, `steel_plates/` folders, which breaks the repo rule "one copy only (archive or extracted files, not both)". Delete one side.
3. **15 archives have no loader.** `scripts/load_spadc_data.py` covers only the six extracted datasets; the rest need a generic `load_uci_zip(folder)` helper.
4. **`data/README.md` is stale.** It documents only the six SpaDC datasets; the card should list all candidates and mark the three chosen ones.

## Next actions (ordered)

1. Extract AI4I + write `load_ai4i()`; verify the leakage trap by fitting a tree with and without the mode flags.
2. Write `docs/01-problem-statement.md` for Hydraulic (decision-maker, cost of error, success threshold).
3. Fix `data/README.md` and de-duplicate the three archives.
4. Prepare the figure list for the three chosen datasets (sensor curves / PCA-by-batch / confusion matrices).
