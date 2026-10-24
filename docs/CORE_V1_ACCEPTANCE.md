# SpecForge 精简核心 v1 实施记录

已在 `/home/zhang/projects/ai/SpecForge` 并行实现新版，旧运行时、共享规格和旧技能入口保持原样。模板维护源仍是 `E:/Project/Zhang/openclaw-codegen/templates/admin-platform`。

## 验收结果

- 新核心单元测试：27/27。
- 生成项目 Maven clean verify、前端冻结依赖安装、类型检查、生产构建：通过。
- 独立 Compose 四服务：通过；45 项 API 检查全部通过。
- 真实 Chromium：管理员创建设备、申请人提交、管理员批准及归还、只读限制、无权限路由拒绝全部通过。
- 同设备并发批准：仅一笔成功；另一笔返回“设备已被借用”。JDBC 显式事务、设备行锁、状态条件更新与数据库唯一索引共同保证。
- 交付 ZIP：逐文件哈希与压缩包完整性检查通过，不含私有环境、运行密钥和依赖目录。
- 本轮验收容器、数据库/Redis/上传/签名卷全部清理；原 preflight 服务保留。

运行编号：`20261024T055251-5fec059bac`。
交付包 SHA-256：`6352eb07e733f4908beffa4674fe3c56dc05626acc936dad0143c5b5340641f3`。

## 代码入口

- `specforge/`：规格校验、生成、工作区、验证、修复、发布和 CLI。
- `examples/device_borrow.yaml`：覆盖全部首轮字段类型的设备借用规格。
- `tests_core/`：独立测试夹具、生成一致性、发布防篡改及失败清理回归。
- `tools/run-core-windows.ps1`：本机 Windows/WSL 一条命令执行及隐藏浏览器工作进程。
- `docs/CORE_V1.md`：完整合同、命令和诊断说明。
- `docs/core-evidence/`：旧版基线和本轮验收摘要。

## 再次运行

WSL 已有工具链、PyYAML 和 Python Playwright/Chromium 时，从 SpecForge 根目录执行：

```bash
python3 -m specforge run \
  --workspace /home/zhang/.local/state/specforge-core/device-borrow \
  --spec examples/device_borrow.yaml \
  --acceptance-pack device-borrow \
  --template /mnt/e/Project/Zhang/openclaw-codegen/templates/admin-platform
```

当前机器的浏览器使用 Windows 已有 Node/Playwright/Chrome；下载旁边的 `run-specforge-core.ps1` 后在 PowerShell 执行即可复现完整流程。可通过参数覆盖路径、发行版、规格、工作区和浏览器依赖。脚本默认调用上述 WSL 仓库，文件复制到任意 Windows 目录仍可运行。

`verify --build-only` 只做构建，不允许发布。`verify --reuse-build` 会核对源码和产物哈希，再完整重跑隔离 API/浏览器验收。`package` 仅接受完整验收通过且哈希未改变的运行。

## 当前边界

首轮业务验收包面向设备借用；其他合法规格可生成和构建，新增领域需要补充对应的业务验收包后才能发布。尚未接入自然语言、模型修复或已有项目增量升级。自动修复仅包含有回归测试的确定性规则。

旧版测试基线仍是 25 项中 12 项通过、10 项失败、3 项报错，已独立记录；本轮没有把它们混作新版验收结果。

所有修改尚未提交 Git。

后续维护性审查及整改见 CORE_V1_REVIEW.md；本文保留首轮验收记录。
