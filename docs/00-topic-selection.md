# 00 · Topic and Dataset Selection

**Status:** in progress  
**Owner:** TBD  
**Decision deadline:** 2026-11-26  
**Linked from:** `README.md` § Topic and dataset selection

## Course constraints

- The topic must be related to industrial data analytics.
- A public dataset (Kaggle, Tianchi, or another public source) or a self-defined industrial problem is acceptable.
- The topic must support the full rubric: problem statement, preprocessing, modeling, model selection, evaluation, and interpretation.

## Candidates

| # | Dataset / problem | Source | Industrial relevance | Task type | Size | License / access | Baseline in one day? | Main risk | Score (1–5) |
|---|---|---|---|---|---|---|---|---|---|
| A | | | | | | | | | |
| B | | | | | | | | | |
| C | | | | | | | | | |

Scoring: 5 = strong, 1 = weak. Weight industrial relevance and feasibility highest; a strong dataset we cannot finish scores zero.

Full candidate list: `data/DATASETS.md` (15 UCI datasets) and `docs/data-sources.md` (6 teammate datasets). Shortlist the top five here.

## Voting (3-2-1)

Each member assigns **3 points** to their first choice, **2** to their second, and **1** to their third. Sum across members; the highest total wins. Record the tally here.

| Member | 3 pts | 2 pts | 1 pt |
|---|---|---|---|
| | | | |

Tie-break: prefer the dataset that covers more SMMG3050 units (data understanding, preprocessing, association/correlation, classification, clustering, visualization); if still tied, prefer the one with the clearer industrial decision.

## Screening questions

1. **Industrial relevance.** Which process, asset, product, or operation does this affect? Who would use the result?
2. **Access and license.** Is the data legally obtainable? Can we publish code without redistributing restricted data?
3. **Label quality.** Is the target measured independently, or derived from features (leakage)?
4. **Feasibility.** Can we load the data, build a baseline, and produce a first metric within one day?
5. **Interpretability.** Can we explain the result to a non-ML audience with two or three figures?
6. **Reproducibility.** Can a teammate or the TA obtain the same data and rerun the pipeline?
7. **Course fit.** How many SMMG3050 units can this dataset support: data understanding, preprocessing, association/correlation, classification, clustering, visualization?

## Decision

- **Chosen dataset / problem:**
- **Why this one:**
- **Why not the runner-up:**
- **Fallback if access fails:**
- **Dataset card:** `data/README.md`
- **Decided by / date:**
