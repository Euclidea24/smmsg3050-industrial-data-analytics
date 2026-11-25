# 00 · Topic and Dataset Selection

**Status:** in progress（已产生推荐排序，待组内投票确认）
**Owner:** TBD
**Decision deadline:** 2026-11-26
**Linked from:** `README.md` § Topic and dataset selection

## Course constraints

- The topic must be related to industrial data analytics.
- A public dataset (Kaggle, Tianchi, or another public source) or a self-defined industrial problem is acceptable.
- The topic must support the full rubric: problem statement, preprocessing, modeling, model selection, evaluation, and interpretation.

## Candidates

按推荐顺序排列（第 1 名最推荐）。已对 `data/raw/` 下全部 18 个数据集做实际读取体检（规模、缺失率、格式），完整扫描记录见下方“筛选范围”。

| # | Dataset / problem | Source | Industrial relevance | Task type | Size | License / access | Baseline in one day? | Main risk | Score (1–5) |
|---|---|---|---|---|---|---|---|---|---|
| A（推荐 1） | **AI4I 2020 机器故障预测**（UCI 601，`data/raw/601-ai4i+2020+predictive+maintenance+dataset/`） | UCI | 高：预测性维护，机床故障 | 分类（含 5 种故障类型标签） | 10,000 × 14 | CC BY 4.0，已入库 | 是：零缺失，字段有物理意义，当天可出基线 | 故障类型标签（TWF/HDF/PWF/OSF/RNF）与主标签存在泄漏风险，建模前需剔除 | 5 |
| B（推荐 2） | **联合循环电厂发电量预测**（UCI 294，`data/raw/294-combined+cycle+power+plant/`） | UCI | 高：电厂能源生产 | 回归 | 9,568 × 5 | CC BY 4.0，已入库 | 是：全仓库最干净，4 特征 + 1 目标 | 特征太少，预处理章节可能偏薄，需在特征工程上补深度 | 4 |
| C（推荐 3） | **钢板缺陷分类**（UCI 198，`data/raw/198-steel+plates+faults/`，已解压副本在 `steel_plates/`） | UCI | 高：钢铁表面质量检测 | 多分类（7 类缺陷） | 1,941 × 34 | CC BY 4.0，已入库 | 是：零缺失，one-hot 标签转单标签即可 | 类别不平衡；27 特征适合做特征排序，贴合 Wang 2022 框架 | 4 |

Scoring: 5 = strong, 1 = weak. Weight industrial relevance and feasibility highest; a strong dataset we cannot finish scores zero.

## 筛选范围与未入选说明

2026-11-25 对 `data/raw/` 全部 18 个数据集逐一读取检查（AI 辅助，已在 docs/09 登记）。未进入前三的主要原因：

- **非工业场景**：wine quality（食品）、dry bean（农业）、wholesale customers（商业）、seoul bike（交通）、concrete（建材）
- **工业但不够轻松**：SECOM（590 特征 + 4.5% 缺失 + 6.6% 极度不平衡，上限最高但工作量最大，仓库已有 `scripts/spadc_quickstart.py` 支持）、gas drift（libsvm 特殊格式 + 概念漂移）、hydraulic（5 个标签列 + 完整数据 530 MB 需另下）
- **需额外处理时间结构**：appliances、849 得土安电力、851 钢铁能耗（含类别变量）
- **太简单撑不起评分点**：wholesale customers（440 条）
- **时间序列额外工作量**：sensorless drive（58,508×49，量大）

## Screening questions

1. **Industrial relevance.** Which process, asset, product, or operation does this affect? Who would use the result?
2. **Access and license.** Is the data legally obtainable? Can we publish code without redistributing restricted data?
3. **Label quality.** Is the target measured independently, or derived from features (leakage)?
4. **Feasibility.** Can we load the data, build a baseline, and produce a first metric within one day?
5. **Interpretability.** Can we explain the result to a non-ML audience with two or three figures?
6. **Reproducibility.** Can a teammate or the TA obtain the same data and rerun the pipeline?

## Decision

- **Chosen dataset / problem:** TBD（推荐顺序 A > B > C，待组内投票）
- **Why this one:**
- **Why not the runner-up:**
- **Fallback if access fails:**
- **Dataset card:** `data/README.md`
- **Decided by / date:**
