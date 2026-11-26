# 10 · Methods Plan（方法计划）

- **Status:** plan — 未运行；除标注“已核对”的审计事实外，所有模型指标、图、规则和聚类结果均为“待运行”
- **Date:** 2026-11-25
- **Owner:** TBD
- **Scope:** AI4I 2020 主方案；SECOM 条件备选；不并行
- **Upstream:** `docs/00-topic-selection.md`、`docs/01`–`05`
- **Rule:** 本文是方法与实验设计，不是结果报告。凡写“待运行”的单元格，均未执行。

## 1. 目的与范围

### 1.1 目标

在 AI4I 2020 上建立一个无泄漏、可复现的故障预警流程：以 AP/PR-AUC 为主指标，比较常数基线、Logistic Regression 和浅 CART 在原始特征/物理构特征、无权/类权重下的 8 格表现；用训练集内的分层 5 折 CV 选模并在折外定阈值，锁定测试集后只评估一次；最后给出可解释的误报/漏报分析。

### 1.2 数据集角色

| 角色 | 数据集 | 规模与关键事实 | 启动条件 | 本计划中的用途 | 明确不做 |
|---|---|---|---|---|---|
| 主方案 | AI4I 2020（UCI 601） | 10,000 × 14；339 正例（3.39%）；0 空值；5 个故障标志取 OR 为 348，与原标签有 27 行不符 | 默认 | 数据审计、8 格矩阵、AP 评估、解释 | 不把 `UDI`、`Product ID`、`TWF`、`HDF`、`PWF`、`OSF`、`RNF` 入模；不做时间序列或 RUL |
| Depth alternate | SECOM（UCI 179） | 1,567 × 590；104 正例（6.64%）；4.54% 缺失；116 个常量列（非 NaN 值唯一即常量列，`dropna=True`） | 仅在 AI4I 主结果冻结后启动，或 AI4I 被判定不可用时替换；不与 AI4I 并行 | 时间切分、SpaDC 与单变量排序对照、Isolation Forest、聚类 | 不套 AI4I 的 8 格；不因 SECOM 拖延主交付 |
| 方法启发 | Du, Zhang & Ou (2022) | 57 个顺序太阳电池样本，全部用于建模与监控验证；传感曲线；连续 SCE | 不选为数据集 | 借“物理构特征 + 相关性排序”的思路 | 不套曲线模型、非线性回归或控制图 |
| 展示借鉴 | Yang (2012) | 重排热图思路 | 可选 | 相关热图的变量重排展示 | 仅借展示方式，不作统计证据；书目信息待核 |

### 1.3 课程单元对应关系

| 单元 | 课程内容 | 本项目落点 | 依据 |
|---|---|---|---|
| U1 | KDD 流程、数据挖掘任务、问题定义 | §1 目标与边界；§3 步骤 1–2 审计与泄漏隔离 | `../_inbox/smmg3050/course_text/unit1_intro.txt` |
| U2 | 数据对象、描述统计、相似性、散点图、箱线图 | §3 步骤 4 的 EDA；散点矩阵与相关热图 | `../_inbox/smmg3050/course_text/unit2_data.txt` |
| U3 | 清洗、缺失、集成、归约、变换、离散化 | §3 步骤 2 和 5；Apriori 的训练折分箱 | `../_inbox/smmg3050/course_text/unit3_preprocessing.txt` |
| U4 | 频繁项集、Apriori、support/confidence/lift | §2 的可选 Apriori；只做解释，不进主模型 | `../_inbox/smmg3050/course_text/unit4_mining.txt` |
| U5 | CART、模型评估、分层 CV、混淆矩阵、类不平衡 | §3 步骤 6–9；§4 8 格矩阵；§5 评估协议 | `../_inbox/smmg3050/course_text/unit5_tree.txt`、`unit5_others.txt` |
| U6 | K-means、层次聚类、DBSCAN、聚类评估 | §2 的可选聚类与稳定性分析 | `../_inbox/smmg3050/course_text/unit6_clustering.txt` |

论文锚点：SpaDC 见 Wang et al. (2022)，DOI `10.1080/00401706.2021.2020171`；物理构特征与相关性排序参考 Du et al. (2022)，DOI `10.1080/00224065.2021.1983491`；Yang 2012 只借重排热图展示思路。

### 1.4 边界与非目标

- **不是已跑结果。** 本文中的 AP、precision、recall、F1、轮廓系数、规则 lift 等均待运行。
- **AI4I 无时间戳。** `UDI` 只是行号，不能构造真实时间切分；主方案用分层随机切分，并在限制中说明。
- **不把五个故障标志当特征。** 它们由过程变量派生，取 OR 与原标签有 27 行不符；保留它们会造成标签泄漏和口径混乱。
- **不把 Du 2022 的曲线模型/控制图套到 AI4I。** AI4I 是合成二分类快照，不是 57 条顺序传感曲线，也没有连续 SCE。
- **SpaDC 不在 AI4I 上强加。** AI4I 只有 5 个传感量加 Type，维度低；SpaDC 的多样性规则没有发挥空间，且其原始设定针对连续质量变量。SpaDC 只在 SECOM 折内与单变量排序比较。
- **不做因果声明。** 只报告预测关联、特征重要性和错例模式；不写“调整某传感器可降低故障”。
- **不做 SMOTE 或过采样。** 主矩阵只比较无权与 `class_weight='balanced'`，避免扩大实验面和引入额外的折内泄漏风险。

## 2. 方法目录

下表覆盖 U1–U6、选模、评估、解释和 SECOM 条件项；各行按方法阶段标注。“AI4I 怎么用”是计划动作，不是已得到的结果。

| 方法 | 解决什么问题 | AI4I 怎么用 | 课件/论文依据 | 风险 |
|---|---|---|---|---|
| U1 · KDD 流程与问题定义 | 把“减少非计划停机”转成可验证的二分类与决策口径 | 一行 = 一台机器的运行快照；目标 = `Machine failure`；明确漏报与误报的代价 | `unit1_intro.txt` | 目标口径漂移；把“故障已发生”误写成“提前预测” |
| U1 · 数据审计 | 行数、列类型、标签、重复、缺失、常量、ID 与泄漏列 | 10,000 × 14；339 正例；0 空值；5 个标志 OR 为 348、与标签 27 行不符；清洗 BOM 表头 | `unit1_intro.txt`、`unit2_data.txt`、`data/DATASETS.md` | 把派生标志当特征；ID 被模型记忆 |
| U2 · 描述统计 | 分布、量纲、离群、类别不平衡 | 5 个传感量加 Type 的 count/mean/sd/min/median/max；按标签分层 | `unit2_data.txt` | 合成数据的分布不代表真实产线 |
| U2 · 散点图与箱线图 | 变量关系、离群点、类别差异 | 传感量两两散点，按 failure 着色并抽样或加透明度；Type 分组箱线图 | `unit2_data.txt` | 点过密遮挡；视觉相关被误读为因果 |
| U2 · 相关热图（含重排） | 冗余与共线结构，辅助物理构特征 | Spearman 矩阵；层次聚类重排变量顺序；图注标样本数 | `unit2_data.txt`、`unit3_preprocessing.txt`（热图为展示形式扩展；课程只讲相关系数分析）；Yang 2012 仅借重排展示 | 相关非因果；合成数据的相关结构人为 |
| U3 · 清洗与缺失/常量检查 | 保证入模矩阵合法、无泄漏 | 删除 `UDI`、`Product ID`、`TWF`、`HDF`、`PWF`、`OSF`、`RNF`；断言无缺失、无常量、无重复；保留 5 个传感量和 Type | `unit3_preprocessing.txt`、`docs/00-topic-selection.md` | 误删目标或误留泄漏列 |
| U3 · 编码 | 类别变量转数值 | Type 做 one-hot，`drop='first'`，只保留 2 个哑变量；编码器只在训练折 fit | `unit3_preprocessing.txt` | 全量编码造成折间泄漏；类别顺序被误当数值 |
| U3 · 缩放 | LR 收敛与系数可比；树不需要 | 数值列 `StandardScaler`，只在训练折 fit；CART 不缩放 | `unit3_preprocessing.txt` | 全量 fit 泄漏；树解释仍应使用原单位 |
| U3 · 离散化 | 为 Apriori 提供可读项集 | 每个数值特征按训练数据三分位分箱；Apriori 用训练集，CV 内则折内重算；保存箱边界 | `unit3_preprocessing.txt` | 边界泄漏；稀有箱导致规则不可信 |
| U2/U3 · Spearman 相关 | 单变量秩相关筛查与对照 | 5 个传感量加温差、功率与标签的 Spearman；只作描述和对照，不据此选模 | `unit2_data.txt`、`unit3_preprocessing.txt`（Pearson 在课程内；Spearman 为课程外补充） | 非线性或交互漏检；二值标签 ties 多 |
| U5 · 折内置换重要性 | 模型无关的特征重要性 | 在每折验证集置换特征，报告 AP 下降的均值±SD；LR 与 CART 同做 | 课程外补充（scikit-learn `permutation_importance`）；评估框架见 `unit5_others.txt` | 相关特征互相稀释；折间不稳定 |
| 论文 · SpaDC | 非线性加多样性特征排序 | 不在 AI4I 主方案使用；仅在 SECOM 折内与单变量排序比较 | Wang et al. 2022，DOI `10.1080/00401706.2021.2020171` | 需要连续质量变量；AI4I 仅 5 维、二值标签，低维且多样性规则无空间 |
| U4 · Apriori | 可读的故障共现规则 | 训练集分箱后挖 `failure=1` 后件；支持数不低于 30、confidence 不低于 0.60、lift 不低于 1.20；只进解释，不进主模型 | `unit4_mining.txt` | 稀有规则和多重比较；分箱泄漏；规则不等于因果 |
| U5 · 常数基线 | 无信息下限，校准指标解读 | `DummyClassifier(strategy='prior')`；AP 理论值约 0.0339，accuracy 理论值约 0.9661，待运行确认 | `unit5_others.txt` | 只报 accuracy 会误以为模型很好 |
| U5 · Logistic Regression | 线性可加基线、系数方向解释 | L2，`C=1.0`，`lbfgs`，`max_iter=2000`；标准化后入模；输出概率 | 课程外补充（分类框架见 `unit5_tree.txt` 和 `unit5_others.txt`） | 线性或可加假设；概率校准受类权重影响 |
| U5 · 浅 CART | 非线性阈值规则与可解释树 | `criterion='gini'`，`max_depth=4`，`min_samples_leaf=20`；深度不进矩阵调参 | `unit5_tree.txt` | 不平衡下树偏向多数类；折间结构不稳 |
| U5 · 类权重 | 缓解 3.39% 正例的不平衡 | LR 和 CART 的 `class_weight='balanced'`；与无权组成 8 格 | `unit5_others.txt` | 概率被抬高；阈值不能固定 0.5；可能增加误报 |
| U5 · 阈值选择 | 把概率转成告警 | 在池化 OOF 预测上最大化 F1；另报 recall 不低于 0.80 的运行点；阈值冻结 | `unit5_others.txt` | 测试集调阈值等于泄漏；F1 不反映误报成本 |
| U5 · 分层留出 | 最终无偏评估 | 70/30 分层；训练 7,000 行约 237 正例，测试 3,000 行约 102 正例；测试索引冻结 | `unit5_others.txt` | 单次测试方差大；测试集正例少 |
| U5 · 分层 5 折 CV | 选模与不确定性 | 训练集内 5 折分层，3 个种子 42/2026/3050；每格 15 个折外 AP | `unit5_others.txt` | 折间泄漏；挑种子；15 个分数并不独立 |
| 选模 · 8 格矩阵 | 同时比较模型、特征、权重 | LR/CART × 原始/加温差与功率 × 无权/类权重；另加常数基线 | 本计划 §4；`unit5_others.txt` | 多重比较和选择偏差；测试集只看一次 |
| 评估 · AP/PR-AUC | 不平衡数据的主指标 | 主指标；OOF 均值±SD；测试集 AP 加 bootstrap 95% CI | 课程 ROC/AUC 见 `unit5_others.txt`；PR-AUC 补充 Saito & Rehmsmeier 2015，DOI `10.1371/journal.pone.0118432` | AP 对正例数敏感；不能与 ROC-AUC 混报 |
| 评估 · Precision/Recall/F1/混淆矩阵 | 业务可读的单点表现 | 冻结阈值下报 TP/FP/FN/TN、precision、recall、F1；按 Type 分层 | `unit5_others.txt` | 单点阈值掩盖曲线；小样本分段不稳 |
| 评估 · PR 曲线 | 展示全阈值权衡 | OOF PR 曲线加测试集单点，不调参；标注 prevalence 基线 | 同上 DOI；课程 ROC 曲线见 `unit5_others.txt` | 曲线好看但工作点差；测试点被反复观看 |
| 评估 · 误报/漏报计数 | 把指标翻成运维语言 | 测试集 FP/FN 数量与占比；列典型错例的传感器组合 | `unit5_others.txt` | 测试集只有约 102 个正例，计数波动大 |
| U6 · K-means + silhouette | 发现运行工况或故障子群 | 训练集拟合，标准化 5 个传感量加温差、功率；k=2..6 选 silhouette；只解释，不进主模型 | `unit6_clustering.txt`；silhouette 见 Rousseeuw 1987 | 需要预设 k；尺度或离群敏感；合成簇可能是人为 |
| U6 · 跨种子稳定性 | 判断聚类是否可复现 | 不同种子或自助样本的 ARI；报告均值±SD；低于 0.7 不解释 | `../_inbox/smmg3050/course_text/unit6_clustering.txt`（聚类评估框架）+ 课程外补充（ARI, Hubert & Arabie 1985） | 稳定不等于有效；ARI 受簇数影响 |
| U6 · 层次聚类/DBSCAN（可选） | 展示 U6 方法，检查层次或密度结构 | 层次用 1,000 行子样本做 dendrogram；DBSCAN 在 2D PCA 或标准化空间用 k-distance 选 eps，报噪声比例 | `unit6_clustering.txt` | 高维密度退化；DBSCAN 参数敏感；只作辅助图 |
| 解释 · 树路径与错例 | 把模型行为翻成工艺语言 | CART 根节点和高风险叶子；10 个 FP/FN 的传感器组合；与置换重要性交叉核对 | `unit5_tree.txt` | 树路径不唯一；相关特征可替代；不要写成因果 |
| 解释 · 因果边界 | 防止过度声明 | 只写关联和预测；不写“调低温度可减少故障”；合成数据无真实因果 | 课程外方法论约束；`unit1_intro.txt` 只覆盖 KDD 流程 | 答辩被问因果；把特征重要性当干预效应 |
| SECOM · 时间切分 | 尊重样本顺序，避免未来泄漏 | 按标签时间戳排序，前 70% 训练、后 30% 测试；不随机 | `unit5_others.txt`；SECOM 标签文件含时间戳 | 时间漂移；两段正例比例不同 |
| SECOM · 缺失/常量处理 | 590 列高维传感的可用性 | 删除 116 个常量列（非 NaN 值唯一即常量列，`dropna=True`）；4.54% 缺失，中位数填补加缺失指示；只在训练段 fit | `unit3_preprocessing.txt` | 缺失机制未知；指示列膨胀；时间切分后分布变化 |
| SECOM · SpaDC vs 单变量排序 | 高维特征排序对照 | 训练段内按时间分 5 折；折内用 SpaDC 与绝对 Spearman 或互信息排序，取 top-k（k 为 10、20、50）下游同分类器比较 AP | Wang et al. 2022，DOI `10.1080/00401706.2021.2020171` | 二值 Y 适配偏差；计算量约 O(p³)；排序不稳 |
| SECOM · Isolation Forest | 无监督异常基线 | 训练段拟合，污染率预设为训练段正例率（约 0.066）；报异常分数与 fail 标签的 AP/PR | 课程外补充 Liu et al. 2008，DOI `10.1109/ICDM.2008.17` | 无监督分数不等于故障概率；污染率敏感 |
| SECOM · 聚类 | 检查批次或工况结构 | 训练段拟合，标准化并降维后做 K-means 或层次；silhouette 加跨种子 ARI | `unit6_clustering.txt` | 590 维距离集中；降维扭曲结构 |

## 3. AI4I 主 pipeline（10 步）

| 步 | 动作 | 关键设置 | 产物（计划路径） | 完成判据 |
|---|---|---|---|---|
| 1 | 审计与快照 | 读取原始 CSV，按 `utf-8-sig` 去 BOM；记录 SHA-256、行列数、标签计数、标志 OR 与 27 行不符 | `data/interim/ai4i_audit.json`；`reports/tables/ai4i_audit.csv` | 10,000 × 14；339 正例；0 空值；348 个 OR 正例；27 行不符；校验和已记录 |
| 2 | 泄漏隔离 | 删除 `UDI`、`Product ID`、`TWF`、`HDF`、`PWF`、`OSF`、`RNF`；保留 5 个传感量和 Type；目标只取 `Machine failure` | `data/interim/ai4i_clean.parquet`；`configs/ai4i_columns.yaml` | 禁列在 X 中出现次数为 0；y 只来自原标签；原始变量为 5 数值加 Type |
| 3 | 切分与冻结 | 70/30 分层留出；训练集内 5 折分层 CV；3 个种子；保存索引和哈希 | `data/interim/splits_ai4i.json` | 训练与测试互斥，合计 10,000；测试 3,000；折哈希固定 |
| 4 | EDA | 描述统计、缺失/常量/重复检查、Type 计数、散点矩阵、Spearman 热图、标志不符表 | `figures/ai4i_scatter_matrix.png`；`figures/ai4i_corr_heatmap.png`；`reports/tables/ai4i_describe.csv` | 每张图有 n 和单位；审计问题都有处置记录 |
| 5 | 预处理 pipeline | Type one-hot（`drop='first'`，`handle_unknown='ignore'`）；中位数填补作保险；LR 加标准化；所有 fit 在训练折内 | `src/ai4i_pipeline.py`（计划）；`tests/test_ai4i_leakage.py`（计划） | scaler 均值等于训练折均值；测试特征不参与 fit；pipeline 可跑通 |
| 6 | 常数基线 | 用先验概率作为无信息基线 | `reports/tables/ai4i_baseline.csv` | AP 理论值约 0.0339；accuracy 理论值约 0.9661；作为下限记录 |
| 7 | 8 格矩阵 | LR/CART × 原始/扩展 × 无权/类权重；5 折 × 3 种子；保存每折 OOF 预测 | `reports/tables/ai4i_matrix_oof.csv`；`data/interim/ai4i_oof_predictions.parquet` | 8 格 × 15 个折外 AP；各格折哈希一致；无缺失分数 |
| 8 | 选模与阈值 | 按 §4.2 规则选格；池化 OOF 最大化 F1 定阈值；阈值哈希冻结 | `configs/ai4i_selected.yaml`；`data/interim/ai4i_threshold.json` | 选择理由有记录；阈值在测试前冻结 |
| 9 | 锁定测试，只评一次 | 在完整训练集重拟合选中格；测试集评分；AP 加 bootstrap 95% CI；混淆矩阵和 PR 单点 | `reports/tables/ai4i_test_metrics.json`；`figures/ai4i_pr_curve.png`；`figures/ai4i_confusion_matrix.png` | 混淆矩阵合计 3,000；测试时间戳和阈值哈希已记录；没有第二次调参 |
| 10 | 解释、复跑与交付 | 置换重要性、CART 路径、10 个错例；可选 Apriori/聚类；同配置复跑 | `reports/tables/ai4i_importance.csv`；`reports/tables/ai4i_error_cases.csv`；`reports/tables/ai4i_run_manifest.json` | 复跑 AP 差异小于 1e-6；图注检查通过；报告写明因果边界 |

## 4. 8 格实验矩阵

### 4.1 因子与固定设置

- **模型：** Logistic Regression、浅 CART。
- **特征集：** 原始特征 = 5 个传感量加 Type（one-hot 后 7 列）；扩展特征 = 原始特征加 `ΔT` 和 `Power`（one-hot 后 9 列）。
- **权重：** 无权；`class_weight='balanced'`。
- **LR 固定：** L2，`C=1.0`，`solver='lbfgs'`，`max_iter=2000`。
- **CART 固定：** `criterion='gini'`，`max_depth=4`，`min_samples_leaf=20`。
- **预处理：** 中位数填补（保险）；Type one-hot `drop='first'` 且 `handle_unknown='ignore'`；LR 加 `StandardScaler`；CART 不缩放。全部只在训练折 fit。
- **CV：** 分层 5 折 × 3 个种子（42、2026、3050）；每格 15 个折外 AP。
- **不调参：** 8 格内超参数预注册，不做网格搜索；CART 深度和 LR 的 C 只在选模后做敏感性附录，不改变选择。
- **物理构特征：** `ΔT = Process temperature [K] − Air temperature [K]`，单位 K；`Power = Torque [Nm] × Rotational speed [rpm] × 2π / 60`，单位 W。两者都是逐行确定性计算，不依赖标签，不需要拟合，因此可以在切分前计算而不构成泄漏。

| 格 | 模型 | 特征集 | 类权重 | 预设 | OOF AP（待运行） |
|---|---|---|---|---|---|
| C1 | Logistic Regression | 原始（7 列） | 无 | C=1.0，L2 | 待运行 |
| C2 | Logistic Regression | 原始（7 列） | balanced | C=1.0，L2 | 待运行 |
| C3 | Logistic Regression | 扩展（9 列） | 无 | C=1.0，L2 | 待运行 |
| C4 | Logistic Regression | 扩展（9 列） | balanced | C=1.0，L2 | 待运行 |
| C5 | 浅 CART | 原始（7 列） | 无 | depth=4，leaf=20，Gini | 待运行 |
| C6 | 浅 CART | 原始（7 列） | balanced | depth=4，leaf=20，Gini | 待运行 |
| C7 | 浅 CART | 扩展（9 列） | 无 | depth=4，leaf=20，Gini | 待运行 |
| C8 | 浅 CART | 扩展（9 列） | balanced | depth=4，leaf=20，Gini | 待运行 |

| 基线 | 定义 | AP（待运行） | accuracy（待运行） | 用途 |
|---|---|---|---|---|
| 常数先验 | `DummyClassifier(strategy='prior')` | 待运行；理论值约 0.0339（测试集按测试 prevalence） | 待运行；理论值约 0.9661 | 只作无信息下限，不是可部署告警规则 |

### 4.2 选模规则

1. **主排序：** 每折单独计算 AP；取 15 个折外 AP 的均值，均值最高者优先。
2. **近似持平：** 若前两名的均值差小于两者配对折差的 1 个 SD，视为持平；按预设简单度顺序取：原始特征优先于扩展特征，LR 优先于 CART，无权优先于类权重。
3. **再次持平：** 取种子间 SD 更小者；仍相同则取表中编号更小者。
4. **阈值：** 对选中格的池化 OOF 预测最大化 F1，得到主阈值；池化 OOF 跨 3 种子会让同一行重复计权，若不希望重复计权，先按种子各算阈值再取均值；另报 recall 不低于 0.80 的运行点作为代价敏感性分析。阈值写入 JSON 并计算 SHA-256，测试前冻结。
5. **测试：** 只评一次；不得用测试集反选模型、阈值或种子。
6. **报告：** 8 格和常数基线全部报告，不只报冠军；避免事后挑选。

## 5. 评估协议

### 5.1 主指标与辅助指标

| 指标 | 角色 | 计算与报告方式 | 不做什么 |
|---|---|---|---|
| AP/PR-AUC | 主指标 | OOF 15 个折外 AP 的均值±SD；测试集 AP 加 2,000 次分层 bootstrap 的 95% CI | 不用 accuracy 替代；不与 ROC-AUC 混为同一结论 |
| ROC-AUC | 次要指标 | 仅用于和课程 ROC 内容对齐；不参与选模 | 不因 ROC-AUC 高就忽略 PR 曲线 |
| Precision/Recall/F1 | 辅助指标 | 冻结阈值下只报正类（故障）的 precision、recall、F1 | 不把 0.5 当默认阈值 |
| 混淆矩阵 | 辅助指标 | TP/FP/FN/TN 计数和行百分比；合计必须等于测试行数 3,000 | 不只报比例不报计数 |
| PR 曲线 | 展示指标 | OOF 曲线加测试单点；画 prevalence 水平线 | 不用测试曲线调阈值 |
| 误报/漏报计数 | 业务指标 | 测试集 FP/FN 数量与占比；按 Type 分层 | 不在小样本分段上做强推断 |

### 5.2 阈值选择

- 主阈值在池化 OOF 预测上按 F1 最大化选取，不能在测试集上选。
- 类权重会抬高预测概率，因此不能假定 0.5 是合理阈值；必须用 OOF 结果。
- 另报 recall 不低于 0.80 的运行点，展示“少漏报但多误报”的代价；该点同样在 OOF 上确定。
- 阈值 JSON 在测试前计算哈希并冻结；测试后不得修改。

### 5.3 不确定性与基线

- 5 折 × 3 种子给出 15 个折外 AP；报告均值±SD，并说明这些分数并不独立，不用它们做普通显著性检验。
- 测试集 3,000 行、约 102 个正例；AP 的 bootstrap 95% CI 可能较宽，必须随点估计一起报告。
- 常数先验基线给出 AP 下限（全数据 prevalence 约 0.0339；测试集按测试 prevalence）和 accuracy 上限（约 0.9661），用来说明“仅看 accuracy”会误判。
- 子组样本少于 30 时只作描述，不作推断。

### 5.4 禁止事项

- 禁止只用 accuracy 评价或选模。
- 禁止在测试集上调阈值、选模型、挑种子或反复试跑后择优。
- 禁止把 `UDI`、`Product ID` 或五个故障标志放入特征矩阵。
- 禁止把 OOF 分数当测试分数，或把测试分数当 OOF 分数。
- 禁止把 Du 2022 的曲线模型、非线性回归或控制图直接套到 AI4I。
- 禁止把特征重要性、树路径或规则 lift 写成因果效应。

## 6. Rubric 映射

| 评分项 | 分值 | 支撑步骤/产物 | 对应章节 |
|---|---|---|---|
| Problem statement | 6 | 决策者、漏报/误报代价、目标与成功标准；`docs/01-problem-statement.md` | §1.1、§1.2 |
| Data preprocessing | 4 | 审计表、禁列为零检查、折内编码/缩放/分箱；`reports/tables/ai4i_audit.csv` | §2、§3 步骤 1–5 |
| Modeling | 6 | LR/CART 规格、8 格矩阵、OOF 预测；`reports/tables/ai4i_matrix_oof.csv` | §3 步骤 6–7、§4 |
| Model selection | 3 | 预注册选模规则、选中配置、阈值冻结；`configs/ai4i_selected.yaml` | §4.2 |
| Evaluation | 6 | AP/PR、分层 CV、冻结测试、bootstrap CI、混淆矩阵 | §3 步骤 9、§5 |
| Interpret results | 5 | 置换重要性、CART 路径、10 个错例、因果边界；`reports/tables/ai4i_importance.csv` | §2、§3 步骤 10 |
| Relevance | 20 | U1–U6 全覆盖；Apriori 和聚类可选；SECOM 条件备选 | §1.3、§2 |
| Accuracy | 20 | 泄漏检查、索引互斥、折哈希、复跑一致、测试只评一次 | §3、§9 |
| Writing | 15 | 报告结构、图表清单、每张图的单位/样本数/阈值 | §3 产物、§8.3 |
| Presentation | 15 | 两张主图、11 分钟（3 人）/15 分钟（4 人）彩排、讲清基线与代价 | §7、§8.3 |
| Additional Score | +4 | 其他组展示时的提问参与；不由数据集决定 | — |
| **合计** | **100 (+4)** |  |  |

## 7. 时间表

| 日期 | 里程碑 | 产物 | 门禁（不过就回退） |
|---|---|---|---|
| 11-26 | 审计封存 | 审计 JSON、切分清单、禁列测试；原始文件校验和 | 10,000 行、339 正例、27 行不符已记录；禁列在 X 中为 0；测试索引冻结 |
| 11-27 | 基线与矩阵 dry run | 常数基线、1 个种子的 8 格试跑、修正后的 pipeline | 常数为 0.0339 附近；8 格都能跑通；折哈希一致 |
| 11-28 | 全量矩阵与选模 | 3 个种子的 8 格 OOF AP、选模记录、阈值 JSON | 15 个折外分数齐全；选择规则已执行；阈值已冻结 |
| 11-29 | Go/No-Go 与可选分析 | 可选 Apriori/聚类；回退决定 | 主 pipeline 可复跑；若矩阵未跑通，按 §8.2 砍可选部分 |
| 11-30 | 锁定测试，单次评估 | 测试 AP、bootstrap CI、混淆矩阵、PR 图 | 测试只评一次；混淆矩阵合计 3,000；阈值哈希未变 |
| 12-01 | 写方法与结果 | 报告初稿、图表定稿 | 每个数字能追到产物；没有“待运行”漏进结果段 |
| 12-02 | 复跑与彩排 | 干净环境复跑日志、11 分钟 slides | AP 差异小于 1e-6；彩排不超时；图注齐全 |
| 12-03 | 展示 | 最终 slides | 两张主图能独立讲清问题、方法、结果和限制 |
| 12-04 | 提交 | 报告与代码归档 | 仓库无凭证、无运行产物；提交清单核对完成 |

## 8. 最小可交付与回退

### 8.1 最小可交付（11-29 前）

- 审计表、冻结的切分清单和禁列为零的测试。
- 无泄漏原始特征上的常数基线、LR、CART 同折比较。
- 主指标 AP 的 OOF 均值±SD（测试集单次结果 11-30 产出）。
- 两张主图：PR 曲线、冻结阈值下的混淆矩阵。
- 可复跑的配置、种子和运行清单。

Apriori、聚类、SECOM 都不属于最小可交付；它们只在主交付稳定后追加。

### 8.2 回退触发与顺序

触发条件：11-29 结束时 8 格矩阵仍未跑通；折哈希或索引一致性无法修复；依赖或时间不足以完成主 pipeline。

回退顺序：

1. 砍 Apriori。
2. 砍 K-means、层次聚类、DBSCAN 和稳定性分析。
3. 砍 SECOM；它本来就不与 AI4I 并行。
4. 砍扩展特征和类权重，只保留原始特征的无权比较。

最终回退方案：无泄漏原始特征 + 常数/LR/CART 同折比较 + AP + 两张主图。泄漏检查、冻结测试、AP、混淆矩阵和复跑清单不可砍。

### 8.3 两张主图

- **主图 1：PR 曲线。** OOF 上画常数基线、OOF AP 最高的 LR 格和最高的 CART 格；测试集只画最终选中模型的一个点；标注 prevalence、n、阈值。
- **主图 2：混淆矩阵。** 冻结阈值下的 TP/FP/FN/TN 计数与行百分比；标注 n=3,000、阈值和测试日期。
- 可选第三张：置换重要性或 CART 树；若时间不足，优先保留前两张。

## 9. 风险与验证

### 9.1 风险表

| 风险 | 为什么会发生 | 预防 | 可执行检查 | 通过标准 |
|---|---|---|---|---|
| 标签泄漏：五个故障标志或 ID 入模 | 标志由过程变量派生，且与原标签有 27 行不符；ID 可被记忆 | 建立禁列清单；切分前删除；目标只取 `Machine failure` | `assert set(FORBIDDEN).isdisjoint(X.columns)`；检查 pipeline 输入列 | 禁列在 X 中为 0；y 正例仍为 339 |
| 预处理泄漏：全量 fit | scaler、编码器或分箱在全体数据上 fit | 所有变换放进 `Pipeline`，只在训练折 fit | scaler 均值与训练折均值比较；箱边界按折保存 | 最大绝对差小于 1e-9；测试折不参与 fit |
| 切分或折不一致 | 不同模型用了不同种子或不同折 | 一份 split manifest；所有格共享折索引 | 索引互斥、并集、折哈希检查 | 训练与测试互斥且合计 10,000；同种子折哈希一致 |
| 指标误用 | 常数基线 accuracy 约 96.6%，看起来很好 | AP 为主指标；报告 prevalence；accuracy 只作辅助 | 检查结果表是否都有 AP；检查选模是否引用 accuracy | 选模只看 AP；accuracy 不进入选择规则 |
| 阈值或测试泄漏 | 在测试集上调阈值、反复看结果 | OOF 定阈值；阈值哈希冻结；测试只评一次 | 测试前后 `sha256sum` 阈值文件；测试日志只有一条 | 哈希不变；测试只评一次 |
| Du 2022 不可直接套 | 57 条顺序曲线、连续 SCE、控制图；AI4I 是合成二分类快照 | 只借物理构特征和相关性排序；不写曲线模型 | 检查代码和报告是否出现 SCE、控制图或曲线拟合 | AI4I 代码路径无这些方法；限制段明确写出 |
| SpaDC 与 AI4I 低维不匹配 | SpaDC 面向连续质量变量和高维特征；AI4I 只有 5 个传感量且标签二值 | 不在 AI4I 使用；只在 SECOM 折内比较 | 检查 AI4I 配置是否引用 SpaDC；检查 SECOM 模块是否折内 fit | AI4I 无 SpaDC；SECOM 比较有折内记录 |
| Apriori 稀有规则 | 支持数 1–2 的规则 lift 很大但不可复现 | 训练集分箱；最小支持数 30；最小置信度 0.60；最小 lift 1.20；前件最多 2 项 | 规则表增加 support_count 列；过滤低于 30 的规则 | 报告中没有支持数小于 30 的规则；规则标为探索性 |
| 类权重导致概率失真 | `class_weight='balanced'` 抬高正类概率 | 阈值用 OOF 定；同时报告有权和无权 | 检查阈值是否由 OOF 产生；报告是否含两类结果 | 阈值有记录；不声称概率等于真实故障率 |
| 测试集小、CI 宽 | 测试集约 102 个正例 | 报 bootstrap CI 和 n；子组少于 30 只描述 | 检查测试表和图的 n 与 CI | 点估计和 CI 同时出现；子组不过度推断 |
| 复跑不一致 | 种子、包版本或数据版本漂移 | 固定 requirements、种子和配置；保存运行清单 | 同配置复跑并比较 AP | 同环境同种子 AP 差异小于 1e-6 |
| 主图缺单位、样本数或阈值 | 图注只写模型名 | 图注检查表 | 逐图检查 K、rpm、Nm、min、W、n、阈值 | 两张主图都含单位、n 和阈值 |

### 9.2 可执行检查清单

以下测试文件为计划产物；实现后按命令执行，当前均未运行。

| 检查 | 命令或断言 | 期望 |
|---|---|---|
| 禁列为零 | `pytest -q tests/test_ai4i_leakage.py::test_forbidden_columns` | `set(FORBIDDEN) & set(X.columns)` 为空 |
| 索引互斥 | `pytest -q tests/test_ai4i_leakage.py::test_split_disjoint` | 训练与测试互斥；并集 10,000；测试 3,000 |
| 折哈希一致 | `pytest -q tests/test_ai4i_leakage.py::test_fold_hash_stable` | 同种子下所有格折哈希相同 |
| 变换只在训练折拟合 | `pytest -q tests/test_ai4i_leakage.py::test_scaler_fit_on_train_only` | scaler 均值等于训练折均值 |
| 标签与标志计数 | `pytest -q tests/test_ai4i_audit.py::test_label_counts` | y 正例 339；标志 OR 348；不符 27 |
| 复跑一致 | `pytest -q tests/test_reproducibility.py` | 两次 AP 差异小于 1e-6 |
| 混淆矩阵合计 | `pytest -q tests/test_ai4i_eval.py::test_confusion_matrix_total` | TP+FP+FN+TN = 3,000 |
| 阈值冻结 | `sha256sum configs/ai4i_threshold.json` 测试前后各一次 | 哈希相同 |
| Apriori 支持数 | `assert rules['support_count'].min() >= 30` | 无稀有规则进入报告 |
| 聚类稳定性 | `assert ari_mean >= 0.7` | 低于 0.7 时只报“不稳定”，不解释簇 |
| SECOM 常量列 | `assert len(constant_cols) == 116`（非 NaN 值唯一即常量列，`dropna=True`）；删除后为 0 | 常量列全部删除 |
| 主图元数据 | 人工检查图注 | 单位、n、阈值齐全 |

### 9.3 未执行与待运行

- AI4I 的 8 格 AP、常数基线实测、PR 曲线、混淆矩阵、置换重要性、Apriori 规则、K-means/层次/DBSCAN 结果：**待运行**。
- SECOM 的时间切分、缺失处理、SpaDC 对照、Isolation Forest、聚类：**待运行**，且仅在触发条件满足时启动。
- 本文只核对了原始数据审计事实和课程/论文锚点，没有产生任何模型结果。

## 附录 A · 引用与事实来源

### A.1 课程讲义

以下文本位于仓库上一级工作区 `_inbox/`，未纳入版本控制；克隆后需从课程材料重新抽取。

| 文件 | 用途 |
|---|---|
| `../_inbox/smmg3050/course_text/unit1_intro.txt` | KDD 流程、数据挖掘任务、问题定义 |
| `../_inbox/smmg3050/course_text/unit2_data.txt` | 描述统计、散点图、箱线图、相关分析 |
| `../_inbox/smmg3050/course_text/unit3_preprocessing.txt` | 清洗、缺失、编码、归一化、离散化 |
| `../_inbox/smmg3050/course_text/unit4_mining.txt` | Apriori、support/confidence/lift |
| `../_inbox/smmg3050/course_text/unit5_tree.txt` | CART、Gini、分类基础 |
| `../_inbox/smmg3050/course_text/unit5_others.txt` | holdout、分层 CV、混淆矩阵、precision/recall/F1、ROC、类不平衡 |
| `../_inbox/smmg3050/course_text/unit6_clustering.txt` | K-means、层次聚类、DBSCAN、聚类评估 |
| `../_inbox/smmg3050/course_text/du-2022.txt` | Du et al. (2022) 中文译文；57 个顺序样本与 SCE 背景 |

### A.2 论文

| 文献 | 用途 | DOI |
|---|---|---|
| Wang, Du, Zhang & Shi (2022), Ranking Features to Promote Diversity: An Approach Based on Sparse Distance Correlation, Technometrics 64(3):384–395 | 稀疏距离相关特征排序；仅用于 SECOM 折内对照 | `10.1080/00401706.2021.2020171` |
| Du, Zhang & Ou (2022), Knowledge-infused process monitoring for quality improvement in solar cell manufacturing processes, JQT 54(5):561–572 | 物理构特征与相关性排序的思路；不套曲线模型 | `10.1080/00224065.2021.1983491` |
| Saito & Rehmsmeier (2015), The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets, PLoS ONE 10(3):e0118432 | 不平衡数据下 PR 曲线优于 ROC 的依据 | `10.1371/journal.pone.0118432` |
| Liu, Ting & Zhou (2008), Isolation Forest, ICDM | Isolation Forest 原始方法 | `10.1109/ICDM.2008.17` |
| Rousseeuw (1987), Silhouettes: a graphical aid to the interpretation and validation of cluster analysis, J. Comput. Appl. Math. 20:53–65 | silhouette 系数 | `10.1016/0377-0427(87)90125-7` |
| Hubert & Arabie (1985), Comparing partitions, Journal of Classification 2:193–218 | ARI 的原始方法；用于聚类跨种子稳定性 | `10.1007/BF01908075` |

Yang (2012) 重排热图：仅借用变量重排的展示方式；组内材料未附 DOI，书目信息待核，因此不列入方法依据。

### A.3 已核对的事实

- AI4I 2020：`data/raw/601-ai4i+2020+predictive+maintenance+dataset/extracted/ai4i2020.csv`，2026-11-25 核对，10,000 行 × 14 列，339 个 `Machine failure=1`，0 个缺失单元格；`TWF`/`HDF`/`PWF`/`OSF`/`RNF` 取 OR 为 348，与原标签 27 行不符。
- SECOM：`data/raw/179-secom/extracted/secom.data` 与 `secom_labels.data`，2026-11-25 核对，1,567 行 × 590 列，104 个正例（6.64%），4.54% 缺失，116 个常量列（非 NaN 值唯一即常量列，`dropna=True`）。
- Du et al. (2022) 使用 57 个连续样本；50/7 拆分属于 Wang et al. (2022) 的 case study 1，不在 Du 文中。AI4I 是合成二分类快照，只借物理构特征和相关性排序思路。
- 上述均为审计或文献事实，不是模型结果；所有模型指标待运行。
