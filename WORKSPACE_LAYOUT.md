# SpecForge 工作区合同

## 当前开发入口

| 目录 | 职责 |
|---|---|
| `specforge/` | 新核心、生成资产及显式验收包 |
| `examples/` | 版本 1 YAML 固定业务规格 |
| `tests_core/` | 新核心独立回归测试 |
| `tests_compat/` | 旧入口依赖隔离与调用合同测试 |
| `tools/` | Windows / WSL 运行包装 |
| `docs/` | 当前合同、验收证据、迁移决策 |
| `docs/legacy/` | 旧版操作文档历史归档 |

模板由 `--template` 显式提供，本机使用外部仓库的 `templates/admin-platform`。仓库 `backend/` 是旧模板，不是新核心默认输入。

## 新核心项目工作区

每个项目显式指定独立 `--workspace`，规格与模板输入快照、生成源码、报告和清单位于每轮 `runs/<run-id>/` 下。成功交付包位于 `releases/`。失败运行保留诊断，不替换成功发布指针。不能把生成副本改动当成生成器源码改动。

## 兼容区

`skills/`、`backend/`、`specforge-runtime/` 保留路径及行为。旧主程序保留自动构建，其他旧命令实现位于 `specforge-runtime/legacy_commands/`，由原命令转发。旧版共享规格在 `specforge-runtime/specs/`，日志在 `specforge-runtime/runs/`，仅后端产物在 `specforge-runtime/outputs/`。这些路径不适用于新版。

旧版实验能力现按命令分支导入，默认模拟等旧命令仍依赖其源码，尚不可直接移动。具体调用证据与退出条件见 [迁移清单](docs/LEGACY_MIGRATION.md)。本轮没有清理用户运行记录、生成产物或数据库。
