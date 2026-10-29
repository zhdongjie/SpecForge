# SpecForge 工作区合同

| 目录 | 职责 |
| --- | --- |
| specforge/ | 唯一运行核心、生成资产、业务扩展和验收包 |
| examples/ | 明确YAML业务规格 |
| tests_core/ | 当前核心回归 |
| tools/ | 独立交付验收和Windows/WSL包装入口 |
| docs/knowledge/ | 当前规则、决策和排错 |
| docs/core-evidence/ | 历史及当前验收证据 |
| docs/legacy/ | 仅历史文档，不是可执行入口 |

模板由--template显式提供，使用独立的后台模板项目。项目工作区通过--workspace指定；每轮保留runs/<run-id>/输入快照、源码、报告与清单，通过验收的交付包位于releases/。失败不覆盖上次成功结果。

旧specforge-runtime/、backend/、skills/、tests_compat/已从当前树移除。不再读写旧共享规格或旧outputs/runs路径。此前本地旧目录及其中运行数据已整体转移到仓库外私有归档；不复制回当前版本、不上传GitHub。退役和数据取回说明见 [退役记录](docs/LEGACY_RETIRED.md)。

本机2026-10-29盘点：仓库内没有历史运行工作区；本地sandbox仅保留需求草稿，不是运行工作区。现有运行工作区位于仓库外/home/zhang/.local/state/specforge-core/，无需迁移。硬性路径隔离禁止以后将仓库内目录用作工作区。实际规则见[工作区与交付合同](docs/knowledge/contracts/workspace-release.md)。本地草稿、现有生成项目、Git历史与已发布历史标签保留。
