# SpecForge 第一轮维护性审查与整改

> 历史记录：旧方案已于2026-10-28退役。下文中的旧路径、兼容承诺和命令仅反映当时状态，当前不可执行。

本轮针对上一轮新增核心做收敛，没有新增第二个业务，也没有重写旧运行时。

## 已整改

| 问题 | 改动 | 意义 |
|---|---|---|
| 验证器硬接设备借用函数 | 独立 acceptance_packs/device_borrow；完整运行显式选择验收包 | 增加业务时无需改验证引擎 |
| 浏览器流程有 Python、JavaScript 两份 | 删除 Python 业务流程；保留单份 browser.cjs | 页面变化只维护一套步骤 |
| Windows 运行细节混进业务流程 | 分离通用 browser.py 与 windows_browser.py | 本机兼容逻辑不影响生成规则 |
| 所有失败都尝试修代码 | 按 preflight/backend/install/frontend/compose/api/browser/cleanup 分类 | 环境或验收错误不会误改源码 |
| 旧编译日志可能驱动错误修复 | 核对失败阶段与源码哈希，保留原始错误 | 避免过期日志触发修改 |
| 重试丢失已有构建证明 | 保留通过的构建哈希，构建模式修复仍只验证构建 | 无需因浏览器配置失败反复构建 |
| 扫描依赖目录后才排除 | 遍历前裁剪缓存、拒绝源码符号链接 | 文件清单更快、更可控 |
| 状态 JSON 使用固定临时文件 | 改为唯一临时文件并原子替换 | 避免并发写临时文件互相覆盖 |

CLI 分支也已简化。验收包会在构建前检查业务与页面字段是否兼容；生成和仅构建模式不依赖任何业务包。Java 扩展中的设备专用错误文本已改为通用资源占用提示。

## 本轮验证

- 单元测试：46 项全部通过。
- 从头生成：Maven 验证、前端冻结安装/类型检查/生产构建通过。
- 隔离部署：四服务启动通过；45 项 API 检查全部通过。
- 同一份浏览器脚本：实际完成创建、提交、审批、归还、只读与无权限检查。
- Wheel 安装包：资源位置与独立目录导入检查通过，已删除的重复模块没有混入安装包。
- 交付 ZIP：逐文件哈希检查通过。验收容器和数据卷已清理。

运行编号：`20261024T061338-dba36685f4`。
最新交付包 SHA-256：`489f3e22265f3c031d7a854793555057e60904a2a25340f27d91f510836bf6ab`。

## 后续使用

完整命令现在显式选择验收包：

```bash
cd /home/zhang/projects/ai/SpecForge
python3 -m specforge run \
  --workspace /home/zhang/.local/state/specforge-core/device-borrow \
  --spec examples/device_borrow.yaml \
  --template /mnt/e/Project/Zhang/openclaw-codegen/templates/admin-platform \
  --acceptance-pack device-borrow
```

本机 Windows 用户可运行随附 run-specforge-core.ps1；脚本已默认显式选择 device-borrow。`-ReuseBuild` 会核对源码和产物哈希再完整重跑验收。仅检查构建仍使用 `verify --build-only`，不需要浏览器或验收包。

核心仍位于 `/home/zhang/projects/ai/SpecForge`，完整维护说明见 docs/CORE_V1.md。旧入口和 admin-platform 模板维护源保持原样；所有修改尚未提交 Git。

## 尚未证明的部分

新的 catalog/loan 规格已通过生成层回归，用来确认生成器没有绑定设备实体名称；它不等于第二个业务已完成端到端验收。下一步仍应选择第二个真实业务验证规格表达能力，再决定迁移旧版哪些模块。本轮不增加第二个业务、不接自然语言或模型修复。

后续图书借阅的真实复用验证见 CORE_V1_SECOND_BUSINESS.md；本文保留维护性审查当时的结论。
