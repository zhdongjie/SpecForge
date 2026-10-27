# 发布模板与SpecForge端到端回归

2026-10-27，使用GitHub模板本地提交 `8a5e9cfcb227a6cc5c823876ba154ce197fdbf0d`，从食谱固定规格重新生成到独立工作区。模板源码未改动，生成器运行代码无需修改；没有推送GitHub。

- 新工作区：`/home/zhang/.local/state/specforge-core/template-release-regression-20261027`。
- 模板：`/mnt/e/Project/Zhang/openclaw-codegen/exports/github/springboot3-vue3-vuetify-admin-template`。
- 规格：`examples/recipe_management.yaml`；显式验收包：`recipe-management`。
- 运行：`20261027T063659-428b8db646`。
- 后端、冻结安装、前端类型检查/生产构建、Compose、145项API、13项浏览器和12项需求覆盖全部通过。
- 交付包从全新临时目录独立部署，重复完整145项API、13项浏览器与需求覆盖通过；包完整性、挂载约束和清理检查通过。
- 临时容器、卷、网络与解压目录已清理，日常平台和历史成功包保留。

模板新库不包含本地版本记录表；正式模板自身指南在其 `docs/template/overview.md`。本轮不复制本机验收脚本或历史数据库迁移补丁到发布模板。

结果与输入身份见 [脱敏证据](core-evidence/template-release-regression.json)。归档SHA256：`a7e4640b4355afe100de43e372ca6161cfd70c4516eb5ce730873721c9ca3e7e`。

复跑使用 `tools/run-core-windows.ps1`，显式传入上述Template、独立Workspace、食谱Spec及AcceptancePack；独立部署使用其ReleaseArchive和ReportsDirectory参数。脚本配置与执行方式见 [运行说明](CORE_V1.md)。不要复用日常数据库或覆盖旧运行目录。
