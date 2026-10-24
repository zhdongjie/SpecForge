# C-003 工作区与交付

- 编号：C-003
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/release.py](../../../specforge/release.py)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

每个项目独立工作区；每轮生成新运行目录，保存输入、源码、报告及清单。记录模板文件哈希、可读取 Git 版本与规格哈希。只有完整验收 PASS 且源码和产物哈希未变化才发布。失败及 build-only 不替换成功发布结果。交付包包含 JAR、前端 dist、SQL 与 Compose 部署配置。


独立交付验收使用 [verify-release 工具](../../../tools/verify-release.py)，从全新解压目录启动包内 JAR / dist，不重新运行 Maven、pnpm 或生成器，不挂载原仓库和原生成工作区。校验和与清单用于检测损坏和篡改，不提供数字签名或发布方认证。工具校验部署挂载、项目资源隔离及清理结果；独立报告不修改原发布指针。完整交付要求生成验收和独立部署验收均 PASS。
