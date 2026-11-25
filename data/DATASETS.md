# UCI 工业数据集清单

生成时间（UTC）：`2026-11-25T13:08:22Z`　|　数据集：15 项（成功 15 / 失败 0）　|　总字节：39.89 MB（41,823,870 B）　|　最大单包：325（24.43 MB）

原始压缩包位于 `data/raw/<id>-<slug>/`，可入库；解压结果在其 `extracted/` 子目录，已被 `.gitignore` 忽略。机器可读版本见 `data/datasets_manifest.json`；克隆后运行 `scripts/download_datasets.py` 可重建解压目录。

## 总览

| # | 名称 | id | 任务 | 目标 | 行×列（主表） | 大小 | License | 下载 URL | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | [AI4I 2020 Predictive Maintenance Dataset](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) | 601 | binary_classification | Machine failure | 10,000 x 14 | 509.9 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip` | — |
| 2 | [Steel Plates Faults](https://archive.ics.uci.edu/dataset/198/steel+plates+faults) | 198 | multiclass_classification | derived from last 7 fault-indicator columns | 1,941 x 34 | 98.5 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/198/steel+plates+faults.zip` | — |
| 3 | [SECOM](https://archive.ics.uci.edu/dataset/179/secom) | 179 | anomaly_detection | secom_labels.data column 0 (-1 pass / 1 fail) | 1,567 x 590 | 1.87 MB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/179/secom.zip` | 2 张表 |
| 4 | [Steel Industry Energy Consumption](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption) | 851 | time_series_regression | Usage_kWh | 35,040 x 11 | 470.7 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/851/steel+industry+energy+consumption.zip` | — |
| 5 | [Productivity Prediction of Garment Employees](https://archive.ics.uci.edu/dataset/597/productivity+prediction+of+garment+employees) | 597 | regression | actual_productivity | 1,197 x 15 | 92.9 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/597/productivity+prediction+of+garment+employees.zip` | — |
| 6 | [Wholesale customers](https://archive.ics.uci.edu/dataset/292/wholesale+customers) | 292 | clustering | none (6 annual spending columns) | 440 x 8 | 14.8 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/292/wholesale+customers.zip` | — |
| 7 | [Seoul Bike Sharing Demand](https://archive.ics.uci.edu/dataset/560/seoul+bike+sharing+demand) | 560 | time_series_regression | Rented Bike Count | 8,760 x 14 | 590.1 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/560/seoul+bike+sharing+demand.zip` | — |
| 8 | [Power Consumption of Tetouan City](https://archive.ics.uci.edu/dataset/849/power+consumption+of+tetouan+city) | 849 | time_series_regression | Zone 1 Power Consumption | 52,416 x 9 | 1.34 MB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/849/power+consumption+of+tetouan+city.zip` | — |
| 9 | [Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality) | 186 | regression | quality | 1,599 x 12 | 89.2 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/186/wine+quality.zip` | 2 张表 |
| 10 | [Electrical Grid Stability Simulated Data](https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data) | 471 | binary_classification | stabf | 10,000 x 14 | 2.31 MB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/471/electrical+grid+stability+simulated+data.zip` | — |
| 11 | [Airfoil Self-Noise](https://archive.ics.uci.edu/dataset/291/airfoil+self+noise) | 291 | regression | last column (scaled sound pressure level) | 1,503 x 6 | 58.7 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/291/airfoil+self+noise.zip` | — |
| 12 | [Dataset for Sensorless Drive Diagnosis](https://archive.ics.uci.edu/dataset/325/dataset+for+sensorless+drive+diagnosis) | 325 | fault_diagnosis_multiclass | last column (11 classes) | 58,509 x 49 | 24.43 MB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/325/dataset+for+sensorless+drive+diagnosis.zip` | — |
| 13 | [Combined Cycle Power Plant](https://archive.ics.uci.edu/dataset/294/combined+cycle+power+plant) | 294 | regression | PE | 9,568 x 5 | 3.50 MB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/294/combined+cycle+power+plant.zip` | 5 张表 |
| 14 | [Concrete Compressive Strength](https://archive.ics.uci.edu/dataset/165/concrete+compressive+strength) | 165 | regression | last column (concrete compressive strength) | 1,030 x 9 (expected) | 33.6 KB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/165/concrete+compressive+strength.zip` | 旧 XLS，需 xlrd |
| 15 | [Dry Bean](https://archive.ics.uci.edu/dataset/602/dry+bean+dataset) | 602 | multiclass_classification | Class | 13,611 x 17 | 4.52 MB | CC BY 4.0 | `https://archive.ics.uci.edu/static/public/602/dry+bean+dataset.zip` | 2 张表 |

## 数据集备注

- **1. AI4I 2020 Predictive Maintenance Dataset（id 601）**：目标列 Machine failure；同表另有 TWF/HDF/PWF/OSF/RNF 故障模式指示列。
- **2. Steel Plates Faults（id 198）**：末 7 列 Pastry/Z_Scratch/K_Scatch/Stains/Dirtiness/Bumps/Other_Faults 为 one-hot 指示，需合成类别。 非表成员：Faults27x7_var(documentation)
- **3. SECOM（id 179）**：secom.data 为空白分隔的 590 特征矩阵（缺失记为 NaN）；secom_labels.data 为时间戳 + 标签。 非表成员：secom.names(documentation)
- **4. Steel Industry Energy Consumption（id 851）**：含 CO2、功率因数、无功功率等派生列；时间戳 15 分钟粒度。
- **5. Productivity Prediction of Garment Employees（id 597）**：同时含 targeted_productivity（计划值）；team 为 1-12 编号（类别型）。
- **6. Wholesale customers（id 292）**：聚类基准集；6 个金额列为 Fresh/Milk/Grocery/Frozen/Detergents_Paper/Delicassen。
- **7. Seoul Bike Sharing Demand（id 560）**：逐小时 8760 行；含季节/节假日/天气协变量。
- **8. Power Consumption of Tetouan City（id 849）**：另含 Zone 2/Zone 3 Power Consumption 及天气列。 API num_instances=52417 比数据行数多 1（API 把表头行计入）
- **9. Wine Quality（id 186）**：两个独立表：winequality-red.csv 与 winequality-white.csv（分隔符 ';'），合计 6497 行。 非表成员：winequality.names(documentation)
- **10. Electrical Grid Stability Simulated Data（id 471）**：stabf 为类别标签，stability 为连续裕度目标；12 个连续特征 + 2 个目标。
- **11. Airfoil Self-Noise（id 291）**：无表头文件；5 个几何/气流特征 + 末列声压级。
- **12. Dataset for Sensorless Drive Diagnosis（id 325）**：49 列、约 5.8 万行；末列为 11 类标签（电机负载/故障组合）。
- **13. Combined Cycle Power Plant（id 294）**：目标 PE = electrical energy output；5 个 sheet 为同一批 9,568 条记录的不同排序（PE 值集已独立核对）；建模时取其一以免重复计数。 非表成员：Folds5x2_pp.ods(alternate), Readme.txt(documentation), Readme.txt~(documentation) 5 个 sheet 行列数完全相同（各 9,568×5）
- **14. Concrete Compressive Strength（id 165）**：旧版 XLS 格式；预期 1030 行 x 9 列。 非表成员：Concrete_Readme.txt(documentation)
- **15. Dry Bean（id 602）**：XLSX 含 Dry_Beans_Dataset（13,611×17，带表头）与 Citation_Request（仅 1 行引用文本，无数据行）；Class 为 7 类品种。 非表成员：Dry_Bean_Dataset.arff(alternate), Dry_Bean_Dataset.txt(documentation)

## 多表数据集（逐表记录）

### 3. SECOM（id 179）

| 表文件 | 编码 | 分隔符 | 表头 | 行×列 | 备注 |
|---|---|---|---|---|---|
| `secom.data` | utf-8-sig | whitespace | 否 | 1,567 x 590 | — |
| `secom_labels.data` | utf-8-sig | whitespace | 否 | 1,567 x 2 | — |

### 9. Wine Quality（id 186）

| 表文件 | 编码 | 分隔符 | 表头 | 行×列 | 备注 |
|---|---|---|---|---|---|
| `winequality-red.csv` | utf-8-sig | ; | 是 | 1,599 x 12 | — |
| `winequality-white.csv` | utf-8-sig | ; | 是 | 4,898 x 12 | — |

### 13. Combined Cycle Power Plant（id 294）

| 表文件 | 编码 | 分隔符 | 表头 | 行×列 | 备注 |
|---|---|---|---|---|---|
| `Folds5x2_pp.xlsx` | binary (xlsx = zip/xml) | — | 是 | 9,568 x 5 | sheet=Sheet1 |
| `Folds5x2_pp.xlsx` | binary (xlsx = zip/xml) | — | 是 | 9,568 x 5 | sheet=Sheet2 |
| `Folds5x2_pp.xlsx` | binary (xlsx = zip/xml) | — | 是 | 9,568 x 5 | sheet=Sheet3 |
| `Folds5x2_pp.xlsx` | binary (xlsx = zip/xml) | — | 是 | 9,568 x 5 | sheet=Sheet4 |
| `Folds5x2_pp.xlsx` | binary (xlsx = zip/xml) | — | 是 | 9,568 x 5 | sheet=Sheet5 |

### 15. Dry Bean（id 602）

| 表文件 | 编码 | 分隔符 | 表头 | 行×列 | 备注 |
|---|---|---|---|---|---|
| `Dry_Bean_Dataset.xlsx` | binary (xlsx = zip/xml) | — | 是 | 13,611 x 17 | sheet=Dry_Beans_Dataset |
| `Dry_Bean_Dataset.xlsx` | binary (xlsx = zip/xml) | — | 是 | 1 x 1 | sheet=Citation_Request |

## 下载与校验

统一命令：`curl.exe -fL --retry 2 --max-time 180 --max-filesize 50000000 -o <zip> <url>`，请求间隔 1.5 s。每个压缩包均通过 `zipfile.ZipFile(...).testzip() is None` 校验，解压前检查成员路径（拒绝绝对路径、盘符、`..`、符号链接），仅解压到各自 `extracted/` 子目录，未执行包内任何脚本。

| # | id | zip 校验 | 成员数 | 展开大小 | SHA256（前 16 位） |
|---|---|---|---|---|---|
| 1 | 601 | ok | 1 | 509.8 KB | `f601f14294bcf190` |
| 2 | 198 | ok | 2 | 292.9 KB | `cb8eb9859198b63f` |
| 3 | 179 | ok | 3 | 5.18 MB | `eea568baf3c22290` |
| 4 | 851 | ok | 1 | 2.60 MB | `d82d28b33780ff15` |
| 5 | 597 | ok | 1 | 92.7 KB | `446026846b37d738` |
| 6 | 292 | ok | 1 | 14.7 KB | `647e6a61683ed23f` |
| 7 | 560 | ok | 1 | 590.0 KB | `139e9908f0a3544b` |
| 8 | 849 | ok | 1 | 4.03 MB | `3c4bf68416118093` |
| 9 | 186 | ok | 3 | 343.7 KB | `3ed56667f4b82824` |
| 10 | 471 | ok | 1 | 2.31 MB | `32eeb20cf1877127` |
| 11 | 291 | ok | 1 | 58.6 KB | `5c7767ba53ad827d` |
| 12 | 325 | ok | 1 | 24.43 MB | `fbce04b326362156` |
| 13 | 294 | ok | 5 | 3.58 MB | `cc7b2a4977c0a44e` |
| 14 | 165 | ok | 2 | 125.7 KB | `dad85d14de8aee4e` |
| 15 | 602 | ok | 4 | 6.54 MB | `0a64eff5be87f48c` |

Fallback 使用情况：未使用（15 个主项全部成功）；未启用池：[374, 242, 352]。

## 说明

- `license` 取自 UCI 数据集页面标注；本批 15 项均为 CC BY 4.0。
- 表头判定：逐列比较首行与后续行的类型（数值/文本），类型不一致的列 ≥30% 才判为有表头；无表头文件（198、179、291、325）首行计入数据行。
- 165 为旧版 XLS，当前解析环境无 `xlrd`，行列数按预期值（1,030×9）记录，未另装依赖。
- 删除对应 zip 可强制重新下载并比对上游更新；否则完好的 zip 会被复用。
