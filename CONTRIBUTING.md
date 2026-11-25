# 协作规则

3–4 人，2026-11-28 硬截止，public 仓库。只保留会影响结果的规则；技术栈和数据集未定，不预设立场。

## 分支与 PR

- 所有改动从最新 `main` 开短分支，分支名 `<名字>/<主题>`，例如 `junbin/topic-choice`。
- 改完推分支、开 PR，`base` 选 `main`；按 [PR 模板](.github/pull_request_template.md) 写清改动和验证。
- 影响共享结果、代码或报告正文的改动，至少一名队友看过后再合并；只改错字、链接、格式的 PR 可自检后合并。
- 冲突时在自己分支 `git merge origin/main`，和原作者核对两边意图后再解决。
- 不覆盖队友未提交的改动，不强推 `main`，不用 `reset --hard` 处理未知改动。

## 数据与凭证

- `data/raw/` 的原始数据可以入库；同一份数据只提交一份（原始压缩包或解压后的文件，不要两份都放）。
- `data/interim/`、`data/processed/` 是派生数据，默认不入库；需要共享时另开目录并说明生成方法。
- `.env`、token、模型权重、逐条预测不入库。
- 数据来源、许可证、获取日期、校验和与署名写在 [data/README.md](data/README.md) 和 `data/DATASETS.md`。
- GitHub 单文件超过 100 MiB 会被拒绝，超过 50 MiB 会警告；遇到这种文件用 Git LFS 或外部位置。

## 报告数字复现

- 报告和幻灯片里的每个数字，都必须能由已提交的脚本 + 配置复现。
- 在 [docs/08-reproducibility.md](docs/08-reproducibility.md) 的 Number index 记：数字、提交 SHA、命令、配置、数据校验和、输出键。
- 测试集冻结后不再调参；固定随机种子。
- 跑不出来的数字删掉，不写“大约”“估计”。

## AI 使用

- 课程只允许在 Project 中使用 AI，作业和考试禁用。
- 在 [docs/09-ai-usage-log.md](docs/09-ai-usage-log.md) 记工具、模型、用途和采纳位置；生成的代码要实际运行，文字要核对来源。
- 不编造引用、统计量或结果；不把受限数据粘贴到外部服务。
