# 旧资产迁移与退出清单

盘点日期：2026-10-24。新核心基线提交 `e15669a`。当前核心 65 项测试通过；此前设备借用 45 项、图书借阅 77 项 API 与两套浏览器验收见 `core-evidence/second-business.json`，本次文档整理未重新执行完整容器验收。

## 已确认的调用链

外部仓库 `E:/Project/Zhang/openclaw-codegen`：

- `control/feishu-openclaw-hub/openclaw-dispatcher/dispatcher.py` 设置旧 runner 路径，构建任务传 project-name、requirement、run-id、domain、final-output-dir、force，读取旧 outputs 和 runs。
- `control/feishu-openclaw-hub/docker-compose.yml` 将宿主 SpecForge 挂至 `/work/SpecForge`。
- `feishu-agent/bot.py` 及两份 specforge-runner agent 配置也引用旧命令。`scripts/clean-task-artifacts.sh` 清理旧运行目录；切换时也必须重新界定清理范围。

仓库内部：

```text
run_requirement_project.py
  → check_specforge_workspace.py
  → scaffold_requirement_project.py → 共享 specforge-runtime/specs
  → run_specforge_autobuild.py
    → specforge-runtime/main.py --auto-build
      → HardeningPipeline
        → ProjectCompiler / ProjectAssemblyCompiler
          → IRLoweringPipeline / BackendAssembler / SynthesisPipeline
        → Maven 编译、启动诊断与旧修复规则
      → specforge-runtime/outputs/<project>
```

`main.py` 在模块顶层还导入 DagEngine、MutationEngine、RuntimeExecutor、GoldenValidator、CodegenPipeline 等，故“正常构建未运行某分支”不等于可以删除文件。静态清单 `core-evidence/legacy-import-inventory.json` 保存全部已跟踪旧 Python 文件的哈希、AST 导入和脚本字符串；相对导入保留原形式，不宣称覆盖反射、配置或外部使用。

## 逐类决策

| 资产 | 当前角色 / 调用来源 | 新核心覆盖情况 | 本轮处理 / 后续退出条件 |
|---|---|---|---|
| `skills/specforge-full-project-compiler/scripts/` | 外部 dispatcher、bot、agent 调用及脚本互调 | 明确 YAML 生成闭环已覆盖；自然语言关键词蓝图未接入 | 保留；外部适配器明确换输入合同并验收后停用 |
| 其他 `skills/` | 历史局部生成、bootstrap 与手动使用 | 部分能力已有新实现，未逐一证明等价 | 保留兼容；不得自动迁入新核心 |
| `specforge-runtime/main.py` | 旧 autobuild 子进程入口 | 新 CLI 覆盖新项目完整流程 | 保留；最后一个旧调用方退出后才可移动 |
| `runtime/hardening/` | auto-build 的 HardeningPipeline | 新 verification/release 和有限 repair | 不复制旧修复集合；仅新模板规则有回归测试时迁移 |
| `runtime/platform_compiler/` | Hardening → ProjectCompiler | 新 generate 复用模板基础设施 | 保留旧链；旧 JWT、权限、响应基础设施不迁入新核心 |
| `runtime/ir_lowering/` | ProjectCompiler / assembly | 新 spec 校验与固定映射 | 不迁入推断层；新增规格能力按明确合同实现 |
| `runtime/synthesis/`、`runtime/codegen/` | assembly 与主程序导入 | 通用业务生成已重建 | 旧命名/类型规则仅作参考；不整体复制 |
| `runtime/mutation/` | main 顶层导入和 mutate 分支 | 新核心不支持交付后增量变更 | 冻结兼容；先隔离 main 导入再评估独立历史归档 |
| DAG、scheduler、replay、logical clock、golden、benchmark 等 | main/executor/verifier 相互依赖和历史测试 | 新闭环不需要这些执行模拟能力 | 不进入新版；旧链未隔离前不移动源码 |
| `backend/` | 旧 readiness、build-plan、assembler 模板输入 | 新版显式 admin-platform 模板 | 保留；旧入口停止后才可归档 |
| `specforge-runtime/specs/` | 旧 scaffold 写入、loader/compiler 读取 | 新版每项目规格快照 | 保留旧合同；禁止新版读写该共享目录 |
| `specforge-runtime/tests/` | 历史 25 项基线 | 新 tests_core 独立 65 项 | 保留失败登记：12 通过、10 失败、3 错误；不冒称新版兼容全部旧测试 |
| runs、outputs、cache、sandbox | 用户运行结果与本地证据 | 新版独立 workspace | 本轮不移动、不删除；需按具体项目建立保留与恢复策略 |
| 根 README 与 WORKSPACE_LAYOUT | 人工选择操作入口 | 已改成新版主入口与双工作区合同 | 第一批归档：旧文档存 docs/legacy，原命令及源码不变 |

## 已完成的第一批归档

旧根文档以原始提交 `bbd5aae` 为内容来源，归档到 `docs/legacy/`，增加历史标识、修正相对文档链接；根文档集中说明新版入口，旧调用方仍可找到原命令。源码、外部配置和用户数据均未移动。

这是操作入口收敛，不代表旧运行时体积已经缩减。当前安全收益是新项目不再默认走旧共享规格和仅后端输出路径。

## 下一批实施门槛

1. 若继续独立 SpecForge 路线，先隔离旧 main 的实验分支导入，使用旧 CLI --help、autobuild 依赖导入及原 25 项测试对照验证，不要求顺手修复旧失败。
2. 独立 legacy 命令分组并记录仍在用的调用方；依赖图、历史行为和恢复路径验证后，再归档实验源码。不能仅按文件名判断无用。
3. OpenClaw 不在当前核心范围。只有将来明确要求接回时，才实现 YAML 规格、模板、工作区、验收包、退出码与发布清单适配；不能把自然语言参数静默塞给新 CLI。
4. 旧模板与 runtime 的整体移除在最后进行，需证实没有兼容消费者。本轮不承诺删除日期。
