# 从需求到交付的实施流程

最近核对：2026-10-30。当前 CLI 与需求覆盖门禁已核对；流程审查仍需人工完成。

## 使用入口

新项目先复制 [复用审查表](project-starter/REUSE_REVIEW.md) 和 [需求覆盖样例](project-starter/requirements.yaml) 到独立项目仓库。审查表是实施前的人工记录；YAML 沿用当前覆盖门禁，未填写样例不能通过验收。业务资产、重放脚本与验收留在项目，生成工作区放到源码外。

## 1. 先确定需求，不先缩减到生成器已有选项

保留用户原始需要，逐项建立需求编号、角色 / 操作 / 归属 / 状态矩阵和验收场景。范围调整记录用户明确决定；执行者不能以“生成器还不支持”为理由直接删功能。

## 2. 按本次需求搜索实际模板

读取源码、前端用法、配置、SQL 和已有测试；追踪完整调用链和资源生命周期。知识库只作入口，未记录的能力继续查源码。无需预建穷尽所有能力的模板库。

每项决定为直接复用、适配或业务定制，并记录具体文件和理由。发现模板实现问题也要登记，不能因为接口存在就假定可用。本次实例见 [食谱复用审查](RECIPE_REUSE_REVIEW.md)。

### 模板能力选择速查

下列为已验证模板的源码导航，具体行为以本次显式模板源码为准。使用前检查路径、调用链和配置；老发布标签不一定包含近期能力，缺少时明确报错，不能默默复制另一份。

| 需要 | 模板内首查位置 | 必须同时确认 |
| --- | --- | --- |
| 登录与当前用户 | backend/src/main/java/com/original/authorize/resource/AuthorizeResource.java；core/utils/SecurityUtils.java（同 Java 包根） | 登录态身份，不能信任客户端 userId |
| 操作权限 | frontend/src/composables/useAuthorities.ts；后端 PreAuthorize 实际消费者 | 页面按钮、接口、归属、状态、组合角色分别验证 |
| 分页与响应 | backend/src/main/java/com/original/core/domain/vo/PageVo.java、ResponseVo.java | 沿用字段、分页上限和错误协议 |
| 错误与请求 | frontend/src/plugins/axios.ts、utils/errorApply.ts（同 src 根） | 登录过期、403 路由、字段错误与重复提示 |
| 业务事务 | backend/src/main/java/com/original/core/service/BusinessJdbcContext.java | 平台管理器、同数据源、写入后失败共同回滚 |
| 图片校验与存储 | backend/src/main/java/com/original/system/file/service/ImageValidationService.java；manager/FileManager.java（同 file 根） | MIME 实际内容、大小/尺寸、公开/私有模型、本人归属 |
| 引用与清理 | backend/src/main/java/com/original/system/file/service/FileReferenceService.java、FileLifecycleGuard.java；system/task/process/ClearFileProcess.java（同 Java 包根） | 保存、替换、删除、候选重查、锁与事务 |
| 前端选图 | frontend/src/composables/useFileUpload.ts | 显式数量/类型/大小策略；业务端点、私有预览和删除仍由项目负责 |
| UI 与部署 | frontend/AGENTS.md、docs/template/ui-style.md；deploy/compose.yaml | 真实页面基准、生产产物、配置和数据卷 |

完整公共能力说明维护在模板 docs/template/；SpecForge 只维护接入与验收合同。具体复用证据可参考 [文件生命周期](FILE_LIFECYCLE_REUSE.md)、[事务](TRANSACTION_CONTEXT_REUSE.md)、[前端上传](UPLOAD_REUSE.md)。

## UI生成前的风格审查

在传入模板中读取 frontend/AGENTS.md 及 docs/template/ui-style.md、ui-reference.md、ui-ai-checklist.md。选择真实页面基准，声明复用的布局、控件属性、主题、弹窗和错误处理。不要把“采用Vuetify”当作一致性证明，也不要把存量生成器资产当成设计权威。

功能、权限及状态流必须保持；视觉以同主题同视口截图和人工比对验收，桌面/手机、浅色/深色及空态/错误态分别登记。食谱及通用页面已有整改与回归记录（docs/UI_RECIPE_ALIGNMENT.md、docs/UI_GENERIC_ALIGNMENT.md）。目前没有自动视觉门禁，未来新增页面不能因已有规范就自动算通过。

## 3. 生成基础结构，再补本项目实现

通用规格能够表达的结构继续使用确定性生成；复杂业务可在生成副本的业务扩展位置补代码、页面和测试，不必先注册新的 Python 应用模块。复用基础设施，避免重复发明上传、认证或权限系统。

分阶段执行：generate → 在当前运行源码中完成明确的项目实现和覆盖清单 → verify → package。定制源码、适配补丁与测试应和项目一起版本管理；重新生成会创建新运行，不能假定旧定制会自动迁移。当前 recipe-management 是已有的显式应用实现，不是以后每个项目必须采用的组织方式。

## 4. 对照原需求验收

生成副本 `specforge/requirements.yaml` 列出每项 need、mode、rationale、sources、template_evidence 和 api / browser / stages 标签。标签必须与真实执行报告匹配。缺失、失败或覆盖清单变化都阻止发布；完成结果在 reports/requirements.json。

角色权限不能只数权限字符串；资源不能只测创建接口。至少验证读写隔离、非法状态、并发、失败回滚、替换、移除、删除和清理。测试数量是诊断信息，不是需求完整证明。

## 5. 验证交付包并沉淀知识

通过完整验收后打包；从新目录解压，只用包内生产产物部署，再按同一需求清单验收。清理临时环境，将本次确认的共性方案与问题写入知识库。未知且未完成项明确报告，不能宣布整体完成。

原设备、图书及两个字段变体是固定历史兼容样板。所有新项目必须提供覆盖清单；build-only 仍只用于诊断，不能交付。

## 6. 独立项目的操作顺序

以下使用占位的绝对路径说明 Linux 环境；先替换所有路径和模块名。Windows/WSL 浏览器环境使用 [运行指南](CORE_V1.md) 中的包装入口；不要直接把 Windows 浏览器运行方式套用到 Linux。

```bash
export PYTHONPATH=/absolute/SpecForge:/absolute/project
python3 -m specforge generate --workspace /absolute/runs/project \
  --spec /absolute/project/project.yaml --template /absolute/template
```

从输出取得 run_id 与 source，项目重放脚本对这个生成副本应用代码、需求清单及必要适配，保存补丁和哈希。不要直接编辑源模板，也不要只手改一次生成结果而没有可重放资产。工单的 build.py/deliver.py 是已验证实例，见 [独立项目说明](REPAIR_PROJECT.md)；不要求新项目复刻其业务或迁入核心。

外部验收包由操作者显式指定 python:your_acceptance，提供 validate_spec(spec)、accept(origin, password, project, source, reports) 和 BROWSER_SCRIPT（或模块旁 browser.cjs），函数参数和结果必须按 [接口实现](../specforge/acceptance_packs/__init__.py) 以及 [核心运行说明](CORE_V1.md) 中实际调用约定接入。它是受信任的开发代码，不能从上传的业务规格自动加载；执行环境须能导入该模块。

```bash
python3 -m specforge verify --workspace /absolute/runs/project \
  --run-id RUN_ID --acceptance-pack python:your_acceptance
python3 -m specforge package --workspace /absolute/runs/project --run-id RUN_ID
python3 /absolute/SpecForge/tools/verify-release.py \
  --archive /absolute/runs/project/releases/ACTUAL_ARCHIVE.zip \
  --reports /absolute/reports/independent-project \
  --acceptance-pack python:your_acceptance
```

仅在前一步通过后执行后一步。requirements.yaml 的 sources/template_evidence 是生成副本相对路径，不能写开发仓库绝对路径；api/browser 必须与实际执行的名称完全一致，stages 使用真实检查键（backend/frontend/compose 等）。不能用只通过 compose 代替业务需求验证。新项目不要复用四个历史样板标识来绕过覆盖清单。

### 停止与修复

- 模板能力缺失：核对模板版本与源码；明确升级输入或补项目实现，不继续打包。
- 规格无法表达：保留原需求，用项目代码实现并安排专属验收。
- 需要改认证权限基础设施或出现未知/重复错误：停止自动修复，保留诊断。
- 源码验收通过但独立包失败、清理失败、视觉未验：分别记录，不能写整体交付通过。
- 仅更新文档不需要重跑所有业务部署；更改运行时代码、模板或生成资产时按影响范围回归。
