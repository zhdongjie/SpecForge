# C-003 工作区与交付

- 编号：C-003
- 状态：已采用；工作区路径隔离为硬性检查
- 适用范围：当前SpecForge核心；源码运行、editable及wheel安装
- 最近验证日期：2026-10-29
- 实现：[workspace.py](../../../specforge/workspace.py)、[CLI](../../../specforge/cli.py)、[release.py](../../../specforge/release.py)
- 证据：[路径隔离回归](../../../tests_core/test_workspace_guard.py)、[第二业务验收](../../core-evidence/second-business.json)

每个项目独立工作区；每轮生成新运行目录，保存输入、源码、报告及清单。记录模板文件哈希、可读取 Git 版本与规格哈希。只有完整验收 PASS 且源码和产物哈希未变化才发布。失败及 build-only 不替换成功发布结果。交付包包含 JAR、前端 dist、SQL 与 Compose 部署配置。


独立交付验收使用 [verify-release 工具](../../../tools/verify-release.py)，从全新解压目录启动包内 JAR / dist，不重新运行 Maven、pnpm 或生成器，不挂载原仓库和原生成工作区。校验和与清单用于检测损坏和篡改，不提供数字签名或发布方认证。工具校验部署挂载、项目资源隔离及清理结果；独立报告不修改原发布指针。完整交付要求生成验收和独立部署验收均 PASS。

## 工作区硬性隔离

所有接受--workspace的CLI命令（包括只读validate）首先调用公共validate_workspace，再解析规格或进入阶段执行。直接调用generate、new_run、resolve_run和package同样检查；Windows运行包装在创建浏览器队列和启动辅助进程之前执行相同预检。没有跳过开关。

- 先展开用户目录并解析绝对路径、符号链接和平台支持的真实路径。
- 工作区不得等于、位于或包含SpecForge源码根目录；源码树通过本项目pyproject身份及核心模块识别，不依赖目录名称或.git存在。
- wheel安装时保护实际specforge包目录；从源码树中运行wheel、或目标指向另一份源码树时，也保护识别出的源码树。不会将整个虚拟环境或site-packages认作源码根。同一环境中的不相交目录可以使用；工作区若包含实际包目录仍拒绝。
- generate/run的工作区与显式模板禁止互相嵌套，保留原有约束。
- 工作区本身的合法外部别名会按真实位置检查，但受管runs、releases不能通过符号链接或junction重定向到别处。

拒绝时不创建工作区、运行目录或发布产物，现有数据不迁移、不删除。仓库内的既有工作区会被拒绝，需要自行迁出后再运行；已位于仓库外且没有重定向的工作区不受影响。全局通用文件工具不承担此业务检查，约束集中在工作区入口。
