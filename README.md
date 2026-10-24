# SpecForge

基于明确业务规格和后台模板生成可独立部署的前后端项目。新项目统一使用 `python -m specforge`；当前提供设备借用、图书借阅验收样板和食谱管理真实应用扩展。

## 开始使用

```bash
python3 -m pip install -e .
python3 -m specforge run \
  --workspace /home/zhang/.local/state/specforge-core/device-borrow \
  --spec examples/device_borrow.yaml \
  --template /mnt/e/Project/Zhang/openclaw-codegen/templates/admin-platform \
  --acceptance-pack device-borrow
```

完整验收需要 JDK、Maven、pnpm、Docker 和浏览器环境。当前 Windows + WSL 环境使用已验证的包装入口：

```powershell
# 在 Windows PowerShell 中运行仓库 tools/run-core-windows.ps1 的本地副本
./run-core-windows.ps1
```

包装脚本的路径与环境配置见 [独立运行说明](docs/CORE_V1.md)。图书借阅改用 `examples/book_lending.yaml`、独立工作区及 `--acceptance-pack book-lending`。

## 工作范围

- 输入：版本 1 YAML 规格和显式模板路径。
- 流程：validate → generate → verify → repair（已知规则、最多两轮）→ package。
- 输出：指定工作区中的独立 `runs/<run-id>/` 与通过全部验收的 `releases/`。
- 新核心代码：`specforge/`；固定样例：`examples/`；回归测试：`tests_core/`。

当前不支持自然语言解析、模型修复和已交付项目增量升级。

## 文档与验证

- [食谱管理系统：真实项目规格与运行](docs/RECIPE_PROJECT.md)

- [工程知识库：规则、决策与排错](docs/knowledge/README.md)
- [知识库与新版交付验证结果](docs/KNOWLEDGE_DELIVERY.md)

- [运行、规格与失败诊断](docs/CORE_V1.md)
- [工作区合同](WORKSPACE_LAYOUT.md)
- [旧资产迁移清单](docs/LEGACY_MIGRATION.md)
- [第二业务与两套系统的验收结果](docs/CORE_V1_SECOND_BUSINESS.md)
- [维护性整改记录](docs/CORE_V1_REVIEW.md)

运行核心测试：`python3 -m unittest discover -s tests_core -q`。

旧入口兼容边界测试：`python3 -m unittest discover -s tests_compat -v`。

## 旧版兼容

`skills/specforge-full-project-compiler/scripts/run_requirement_project.py`、`specforge-runtime/` 和 `backend/` 仍保留原路径。外部 OpenClaw dispatcher 仍调用旧入口，其自然语言输入和仅后端输出合同与新版不同。

旧版操作说明已归档至 [历史 README](docs/legacy/README.md) 和 [历史目录合同](docs/legacy/WORKSPACE_LAYOUT.md)。新项目按上面的新版入口执行；外部适配器切换需另行实现明确规格输入与完整验收合同。
