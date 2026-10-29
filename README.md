# SpecForge

当前版本：[v0.2.1](docs/releases/v0.2.1.md)。仅维护新版 `specforge` 核心。旧方案已退役，默认分支统一使用新版；历史标签仅作历史取证。见 [退役说明](docs/LEGACY_RETIRED.md)。

基于明确业务规格和后台模板生成可独立部署的前后端项目。新项目统一使用 `python -m specforge`；当前提供设备借用、图书借阅验收样板和食谱管理真实应用扩展。

## 开始使用

真实项目先按 [需求到交付流程](docs/GENERATION_WORKFLOW.md) 做需求覆盖与模板复用审查。未登记的能力先查模板源码，不能直接删减需求。

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python3 -m specforge run \
  --workspace /home/zhang/.local/state/specforge-core/device-borrow \
  --spec examples/device_borrow.yaml \
  --template /mnt/e/Project/Zhang/openclaw-codegen/exports/github/springboot3-vue3-vuetify-admin-template \
  --acceptance-pack device-borrow
```

完整验收需要 JDK、Maven、pnpm、Docker 和浏览器环境。当前 Windows + WSL 环境使用已验证的包装入口：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "\\wsl.localhost\Ubuntu\home\zhang\projects\ai\SpecForge\tools\run-core-windows.ps1" `
  -Spec /home/zhang/projects/ai/SpecForge/examples/recipe_management.yaml `
  -Workspace /home/zhang/.local/state/specforge-core/recipe-management `
  -AcceptancePack recipe-management
```

包装入口默认使用已提交的正式模板本地副本；`-Template` 仍可显式覆盖。它会创建新运行记录，不覆盖已有成功产物。

包装脚本的路径与环境配置见 [独立运行说明](docs/CORE_V1.md)。图书借阅改用 `examples/book_lending.yaml`、独立工作区及 `--acceptance-pack book-lending`。

## 工作范围

- 输入：版本 1 YAML 规格和显式模板路径。
- 流程：validate → generate → verify → repair（已知规则、最多两轮）→ package。
- 工作区必须与核心源码/包目录及模板隔离，实际路径重叠会在执行前报错；规则见[工作区合同](docs/knowledge/contracts/workspace-release.md)。
- 输出：指定工作区中的独立 `runs/<run-id>/` 与通过全部验收的 `releases/`。
- 新核心代码：`specforge/`；固定样例：`examples/`；回归测试：`tests_core/`。

当前不支持自然语言解析、模型修复和已交付项目增量升级。

## 文档与验证

- [v0.2.1发布与食谱完整交付回归](docs/V021_RECIPE_REGRESSION.md)

- [发布模板端到端回归](docs/TEMPLATE_RELEASE_REGRESSION.md)

- [食谱管理系统：真实项目规格与运行](docs/RECIPE_PROJECT.md)

- [工程知识库：规则、决策与排错](docs/knowledge/README.md)
- [知识库与新版交付验证结果](docs/KNOWLEDGE_DELIVERY.md)

- [运行、规格与失败诊断](docs/CORE_V1.md)
- [工作区合同](WORKSPACE_LAYOUT.md)
- [旧方案退役与数据保留](docs/LEGACY_RETIRED.md)
- [第二业务与两套系统的验收结果](docs/CORE_V1_SECOND_BUSINESS.md)
- [维护性整改记录](docs/CORE_V1_REVIEW.md)

运行核心测试：`python3 -m unittest discover -s tests_core -q`。


## 维护范围

唯一运行入口是 `python -m specforge` 或安装后的 `specforge`。不提供旧命令包装、共享规格运行时或自然语言输入的静默兼容。OpenClaw/飞书旧生成调用已停用，不能将旧参数直接传给新CLI。

后端和前端基础设施由显式外部模板提供，本仓库不再内置另一份旧后端。既有生成项目、交付包和私有运行记录保留，历史验收报告不作为当前操作指南。
