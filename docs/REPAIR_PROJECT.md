# 报修工单系统：独立项目泛化验证

本页保留首版交付的实现与证据；后续共享图片校验和清理协议已提炼到模板，当前改造见[复用审计](REUSE_COST_AUDIT.md)及[文件生命周期复用](FILE_LIFECYCLE_REUSE.md)。

本项目按用户确认的报修功能清单实施。项目源码位于本机`/home/zhang/projects/apps/repair-workorders`，使用独立Git仓库；没有新增`specforge.applications.repair_*`或内置业务验收包。最终运行结论及输入身份见[结构化证据](core-evidence/repair-project.json)。

## 职责与需求

- SpecForge：通过明确YAML生成分类CRUD、SQL、权限与基本结构；负责构建、隔离部署、需求覆盖和打包。
- 独立项目：保存project.yaml、REQUIREMENTS.md、requirements.yaml、业务SQL/Java/Vue、可重放build.py、完整交付deliver.py及repair_acceptance。
- 模板：继续提供登录账号角色、当前用户、请求错误封装、主题、列表表单、文件元数据/引用/清理及Docker基础配置。

报修人提交标题、故障、地点、分类、紧急程度及多图，查询本人记录、撤销待分派或编辑退回记录；管理员分派、改派或退回；维修人员开始维修、追加记录/图片并提交验收；报修人确认关闭或说明未解决退回维修。只读管理可查全部及附件，不能修改。账号可以组合报修与维修角色；验收资格始终校验实际报修人，管理员身份不自动取得他人验收权。

状态为待分派→待处理→处理中→待验收→已关闭；待分派可撤销/退回，退回修改后重新待分派，验收不通过回处理中。改派回待处理并记录原因；旧维修人失去维修身份带来的该单及附件访问资格；若同时是实际报修人或另有全量查询权限，仍可按该独立身份读取，但不能再作为当前维修人员处理。流转写操作带修订号并在行锁事务中保存状态、记录与附件引用。

支持状态、分类、关键词、日期、分页查询和管理员真实统计。维修人员处理量明确为提交完工次数，不混称唯一关闭工单数。业务UTC存储，界面与日期筛选使用北京时间。分类已有任何工单引用时禁止删除，工单与历史维修记录保留。

首版不包含备件、费用、自动派单、短信、SLA，沿用确认范围。

## 私有附件复用决定

模板FileManager的默认产物是公开静态URL，不满足本项目按工单授权读取的要求。项目复用FileUtils的MIME检测、FileEntity/FileService元数据、FileReferenceService引用和ClearFileProcess清理；图片验证及私有存储/授权下载由本项目实现，未重写模板认证权限基础设施。

附件仅写入独立private-workorders卷，位于公开files树之外。下载接口检查当前角色与工单归属并返回no-store字节；未关联图片仅上传者可预览。客户端只提交图片编号，不能伪造文件路径或关联他人图片。每次最多6张、真实PNG/JPEG各5MB、最大4096×4096。

替换移除时同事务更新引用；未关联删除立即标为不可访问，随后复用真实清理任务回收物理文件。被引用和历史处理记录中的图片继续保留。清理与关联共享文件行锁，并在清理前重查引用。新增卷在Docker镜像中预建并赋予非root应用用户，未通过root运行规避权限。

改动只在生成副本：业务枚举、清理锁、分类删除保护、品牌、私有卷及目录。补丁和前后哈希位于副本specforge/adaptations，项目源码清单也记录哈希。原模板不变。

## 运行与交付

Linux配置浏览器后，一条命令：

```bash
cd /home/zhang/projects/apps/repair-workorders
python3 deliver.py \
  --core /home/zhang/projects/ai/SpecForge \
  --template /mnt/e/Project/Zhang/openclaw-codegen/exports/github/springboot3-vue3-vuetify-admin-template \
  --workspace /home/zhang/.local/state/specforge-core/repair-workorders-delivery
```

本机Windows/WSL使用该项目run-windows.ps1的本地副本（或可执行的共享路径），显式传Workspace；其他机器覆盖RepoRoot/ProjectRoot/Template及浏览器路径。它复用核心浏览器队列协议，隐藏运行辅助进程并在结束后清理。

流程为生成→项目定制→构建及完整API/浏览器/覆盖验收→打包→全新目录独立部署验收。每次创建新运行；失败不替换此前生成成功包。独立部署失败时整体结果FAIL，即使生成阶段已经打包。包内REPAIR_SYSTEM.md说明部署和使用，应用部署无需SpecForge或开发验收模块。

外部验收显式指定`python:repair_acceptance`，使用者提供可信模块环境；其需求、API、浏览器标签与核心覆盖门禁相同。固定项目验收严格核对实体和UI合同，不靠字段名猜业务。

## 验证与经验

功能检查与UI风格分别验证。页面基准为正式模板system/user/index.vue、UserForm/AddUser及ConfirmDialog；沿用主题、pa-4卡片、outlined密度、小型按钮、secondary标题和响应式网格。采集1280×800/390×844、浅/深橙主题下列表、编辑、详情、错误、空态、统计及模板基准截图；截图脚本不是像素相似度门禁，最终视觉判断需人工复核。

本轮暴露并修复的共性问题：外部项目缺少验收接入入口、私有卷初始属主、将HTTP状态误当业务授权结果，以及DATETIME/容器时区隐式转换。外部入口有核心回归；其他修复和故障注入在独立项目中验收。模板公开上传不能直接宣传为私有附件能力，必须追踪物理存储和实际读取路径。


## 最终验收结果（2026-10-29）

| 检查 | 结果 |
| --- | --- |
| 核心回归及实际wheel验收入口 | 112项通过；外部包及四个内置包可加载 |
| Maven、冻结安装、类型检查、生产构建 | PASS |
| 生成API / 浏览器 / 需求覆盖 | 140项 / 14个场景 / 11项，全通过 |
| 独立部署API / 浏览器 / 需求覆盖 | 140项 / 14个场景 / 11项，全通过 |
| 相同输入及定制重放 | 488个构建前源码文件清单一致 |
| 视觉 | 每轮32张；最终人工比对通过，手机主流程实际执行 |
| 模板与清理 | 模板源码未变；本轮所有隔离容器/卷/网络和临时凭据已清理 |

最终运行：`20261029T070324-0a4c05ecf6`。核心实现本地提交`bc72e1b`；独立项目本地提交`11cdf3c`。未新增GitHub发布，历史v0.2.1 wheel不包含外部验收入口。

交付包SHA-256：`d8765a3f33218554f79079e4053fbd0f7beaaa3c6d254fd0f12d3e39f843ccad`。Windows可读副本及项目源码快照位于本机`E:/Project/Zhang/openclaw-codegen/artifacts/repair-workorders/release/`；完整路径、输入身份和截图哈希见结构化证据。验收环境已清理，没有长期运行的工单演示实例，原食谱演示不变。

本轮泛化结论：分类CRUD由通用规格生成；状态流、私有附件与权限组合仍需独立项目明确实现。项目拥有4个业务生产资产文件、1647行（Java、Vue、SQL），并有6个模板副本适配文件及项目重放/验收脚本。记录实际代码量，不虚构人工工时，也不据此宣称任意复杂业务仅凭YAML自动生成。共性的外部验收入口进入核心，工单业务留在独立项目。
