# Data

Raw data may be committed; derived data is not. This directory documents what the data is, where it came from, and how to obtain it.

**当前状态（2026-11-25）：选题阶段。** 组内提出 5 个候选选题，对应 5 个候选数据集。其中 3 个已下载并入库 `data/raw/`（按新规则，原始数据可提交，每份只提交一份），2 个需要账号登录手动下载。最终选定题目后，仅保留对应卡片并把其余移入本节末尾的“未选用”列表。

## Candidate 1 · 航空发动机剩余寿命预测（C-MAPSS）✅ 已下载并入库

| Field | Value |
|---|---|
| Dataset name | NASA C-MAPSS Turbofan Engine Degradation Simulation Data Set |
| Source / URL | NASA Prognostics Data Repository: https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/ （直接下载：https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip ） |
| License / terms | 公开数据集，NASA 未指定许可证；使用时需引用 Saxena & Goebel (2008) 并致谢 NASA PCoE |
| Retrieval date | 2026-11-25 |
| Version / checksum | 见下方“校验和”一节 |
| Size (rows × columns) | train_FD001: 20631×26（100 台）；train_FD002: 53759×26（260 台）；train_FD003: 24720×26（100 台）；train_FD004: 61249×26（249 台）；test 集行数 13096 / 33991 / 16596 / 41214 |
| Target column | RUL（剩余可用循环数，由运行至失效的轨迹推得；test 集真值在 RUL_FD00x.txt） |
| Unit of analysis | 单台发动机 × 单个运行循环（26 列 = 单元号、循环数、3 个工况设置、21 个传感器） |
| Known issues | 传感器含噪声；FD002/FD004 有 6 种工况需先聚类或归一化；readme.txt 为 Windows-1252 编码 |

## Candidate 2 · 机器故障预测（AI4I 2020）✅ 已下载并入库

| Field | Value |
|---|---|
| Dataset name | AI4I 2020 Predictive Maintenance Dataset |
| Source / URL | UCI ML Repository: https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset （直接下载：https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip ） |
| License / terms | CC BY 4.0 |
| Retrieval date | 2026-11-25 |
| Version / checksum | ai4i2020.csv SHA256 `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e` |
| Size (rows × columns) | 10000 × 14 |
| Target column | `Machine failure`（二分类）；故障类型细分列 TWF / HDF / PWF / OSF / RNF |
| Unit of analysis | 单个机器数据点（温度、转速、扭矩、刀具磨损等传感特征） |
| Known issues | 故障标签存在重叠与泄漏风险：TWF/HDF/PWF/OSF/RNF 是故障类型标签，建模时需与主标签区分处理；官方说明 RNF 为随机故障 |

## Candidate 3 · 半导体不良品预测（SECOM）✅ 已下载并入库

| Field | Value |
|---|---|
| Dataset name | SECOM Semiconductor Manufacturing |
| Source / URL | UCI ML Repository: https://archive.ics.uci.edu/dataset/179/secom （直接下载：https://archive.ics.uci.edu/static/public/179/secom.zip ） |
| License / terms | CC BY 4.0 |
| Retrieval date | 2026-11-25 |
| Version / checksum | secom.data SHA256 `20f0e7ee434f7dcbae0eea9ffff009a2b57f42d6b0dc9a5bd4f00782c0a3374c`；secom_labels.data SHA256 `126884cf453705c9e61a903fe906f0665a3b45ce3639e621edc5c93c89627e03` |
| Size (rows × columns) | 1567 × 590 特征 + 标签文件（标签 + 时间戳） |
| Target column | secom_labels.data 第 1 列（-1 = 合格，1 = 不良品） |
| Unit of analysis | 单片晶圆 |
| Known issues | 极度不平衡（不良品 6.64%）；缺失值约 4.54%，部分特征近乎常数；特征匿名无语义 |

## Candidate 4 · 钢材表面缺陷图像分类（NEU）⚠️ 待手动下载（暂缓）

| Field | Value |
|---|---|
| Dataset name | NEU Surface Defect Database（NEU-CLS） |
| Source / URL | Kaggle: https://www.kaggle.com/datasets/kaustubhdikshit/neu-surface-defect-database （原始出处：东北大学，Song & Yan 2013） |
| License / terms | 学术研究用途；Kaggle 页面未指定标准许可证，使用前确认 |
| Retrieval date | 待下载 |
| Version / checksum | 待下载后填写 |
| Size (rows × columns) | 1800 张 200×200 灰度图（6 类缺陷 × 300 张） |
| Target column | 缺陷类别（Cr / In / Pa / PS / RS / Sc） |
| Unit of analysis | 单张表面图像 |
| Known issues | 需要 Kaggle 账号登录才能下载；下载步骤见下方“获取步骤” |

## Candidate 5 · 工业蒸汽量预测（天池）⚠️ 待手动下载（暂缓）

| Field | Value |
|---|---|
| Dataset name | 天池·工业蒸汽量预测（赛题数据） |
| Source / URL | 阿里天池: https://tianchi.aliyun.com/competition/entrance/231693 （“工业蒸汽量预测”赛题页内提供训练/测试数据下载） |
| License / terms | 天池竞赛数据使用协议（需登录并接受赛题条款；注意能否用于课程项目需确认条款） |
| Retrieval date | 待下载 |
| Version / checksum | 待下载后填写 |
| Size (rows × columns) | 训练集约三千条 × 38 个脱敏工况特征（以赛题页为准） |
| Target column | 蒸汽量 target |
| Unit of analysis | 单条锅炉工况记录 |
| Known issues | 需要阿里云/天池账号登录；特征已脱敏无语义；测试集无标签（按排行榜评估） |

## 校验和

C-MAPSS 解压后各文件 SHA256（`data/raw/cmapss/CMAPSSData/`，共 43.2 MiB，含数据集论文 Damage Propagation Modeling.pdf）：

```text
963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8  train_FD001.txt
dac6c4dbc4e7c1bdeb5747da3d313d05c395bb99801b44a002b26a2ba13d788f  train_FD002.txt
2abbe9968cc5e8eb091980f51b20f62bb4127336d3482cb52071d53bf23329e2  train_FD003.txt
27ef6160b6a1dcb2613a88de9c239f763b223f02cdc41dc5cdedc5dc189b6218  train_FD004.txt
3cda7109ce17bafb5443f2ac926cfcf88154b941b8c4cf95eb55d1ddd6f52851  test_FD001.txt
de7b5bf7e998a985c378488480528b7c02cff1406a46740def362dda8d9b4e02  test_FD002.txt
299babd63c8d987cef079c4a425429f33b3a34797d803bbe2ad48c29dbd0d790  test_FD003.txt
1dc675fff0624bac10786927c6715b37d1297657137400d2b1a3138d777a3ba5  test_FD004.txt
a19c8ec94931949d0485bdc35118206e9c81c4547b422efb9cf86f4ceddbceca  RUL_FD001.txt
c851dd96a6ea6998d3c4a8f834d3c8013aa90e93a6ed950dc826ad0655b2906b  RUL_FD002.txt
df1e0566306b174a2de41c67a3e7a51877889598b78643fc3e5685259091b7cb  RUL_FD003.txt
196b836b85a95ac7fdbbf29c5fdf1657382eafa445644d114ffaaf50dc2975e1  RUL_FD004.txt
4f5270554b775c67e73aff383c5436fd329d6e4cc3d3a116913276fae511269b  readme.txt
```

AI4I 与 SECOM 的校验和见各自卡片的 Version / checksum 行。

## Placement

```text
data/raw/        original files (may be committed; one copy only)
data/interim/    intermediate cleaned data (not committed)
data/processed/  model-ready data (not committed)
```

当前布局（均已提交，均为解压后的唯一一份拷贝）：

```text
data/raw/cmapss/CMAPSSData/      ✅ 选题一（13 个文件，43.2 MiB）
data/raw/ai4i-2020/ai4i2020.csv  ✅ 选题二（0.5 MiB）
data/raw/secom/                  ✅ 选题三（secom.data / secom_labels.data / secom.names，5.5 MiB）
data/raw/neu-surface-defect/     ⬜ 选题四（暂缓）
data/raw/tianchi-steam/          ⬜ 选题五（暂缓）
```

## Acquisition

已入库的 3 个数据集可用以下命令复现获取（Windows 可用 Git Bash 执行；校验和见上文）：

```bash
# C-MAPSS（选题一）
curl -L -o cmapss.zip "https://phm-datasets.s3.amazonaws.com/NASA/6.+Turbofan+Engine+Degradation+Simulation+Data+Set.zip"
# 解压后内层还有 CMAPSSData.zip，需再次解压

# AI4I 2020（选题二）
curl -L -o ai4i.zip "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"

# SECOM（选题三）
curl -L -o secom.zip "https://archive.ics.uci.edu/static/public/179/secom.zip"
```

待手动下载的 2 个数据集（需账号登录，暂缓）：

1. **NEU（选题四）**：浏览器打开 Kaggle 数据集页 → 登录 → 点 “Download” 按钮 → 解压。
2. **天池（选题五）**：浏览器打开赛题页 → 登录阿里云账号 → 报名/接受条款 → 在“数据集”页签下载。

## Rules

- Raw data may be committed under `data/raw/`; commit one copy only (archive or extracted files, not both).
- Never commit credentials, personal information, or per-row predictions.
- Record the license, retrieval date, checksum, and attribution before using the data.
- Keep `data/raw/` read-only; write cleaned outputs to `data/interim/` or `data/processed/`.
- GitHub rejects files over 100 MiB and warns above 50 MiB; use Git LFS or an external location for those.

## 未选用

（选题确定后，把未选中的数据集卡片移到本节存档。）
