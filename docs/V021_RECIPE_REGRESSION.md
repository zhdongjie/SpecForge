# v0.2.1 发布与食谱交付回归

2026-10-29。状态：完成。结构化身份、报告及产物位置见[验收证据](core-evidence/v0.2.1-recipe-regression.json)。

## 发布

[v0.2.1](https://github.com/zhdongjie/SpecForge/releases/tag/v0.2.1)已发布，包含源码、wheel及SHA256SUMS。GitHub Actions下载附件校验通过，本机另外下载正式wheel核对摘要、安装并检查版本和业务资产。包内版本与安装元数据均为0.2.1。核心109项测试通过。

## 业务与独立交付

显式使用examples/recipe_management.yaml和独立后台模板仓库f2ef516版本，在新的外部工作区生成；旧演示环境、数据库与上传不变。

| 阶段 | 结果 |
| --- | --- |
| Maven clean verify | PASS |
| pnpm冻结锁文件安装、vue-tsc类型检查、生产构建 | PASS |
| 新运行Compose、API、浏览器 | PASS；145项API、17个浏览器步骤 |
| 原始需求覆盖 | PASS；12项，包含图片生命周期、事务回滚及权限组合 |
| 交付包校验、安全解压、隔离挂载和独立启动 | PASS |
| 独立部署API、浏览器、需求覆盖 | PASS；145项、17步、12项 |
| 两轮容器、卷、网络、临时凭据和解压目录清理 | PASS |

独立部署只使用解压包中的JAR、dist、SQL与部署文件，不调用Maven、pnpm或生成器，不挂载仓库或原工作区。验收工具运行于开发环境，不是应用部署依赖。

相同规格与模板两次重新生成的源码清单完全相同；正式模板清单与运行输入记录一致。构建后仅frontend/src/types/components.d.ts由组件插件增加BusinessPanel声明，已单独核实，不将构建产物与生成源码混作同一确定性比较。

## UI复验

以实际模板system/user/index.vue和AddUser/UserForm为基准，复读模板UI合同。图文列表、食材步骤和统计采用业务布局，导航、卡片、主题、outlined表单、secondary弹窗标题、错误反馈与按钮沿用模板。

在1280×800、390×844以及light-orange、dark-orange四种条件下，各采集九个状态：模板列表/编辑，食谱列表/详情/编辑/错误/空态/统计，以及分类列表，共36张。人工查看联系图及编辑、错误、详情原图；检查范围内未发现阻断风格问题，手机编辑保存/取消可达，无横向溢出。

完整页面截图可能包含固定手机弹窗下方的原页面，另检查844高视口裁剪确认实际操作区域。封面采用验收图片，不是实际菜谱摄影。本轮不是像素相似度自动门禁，不将结果推广到未检查页面或任意未来规格。

截图及本次一次性视觉检查脚本仅保留在本机artifacts/specforge-v0.2.1/，仓库记录哈希与位置；没有新增核心运行时或永久业务模块。本轮未发现需要新增生成规则的业务缺口。

## 交付位置

工作区：/home/zhang/.local/state/specforge-core/v021-recipe-regression-20261029。

运行：20261029T035234-5fa3d437db。

交付包：该工作区releases/recipe_management-20261029T035234-5fa3d437db.zip。

SHA-256：82bec17586dee472b8d64acc0594dc5472c21fbb4e25c99c8df5b8204bd4b2b3。

独立部署报告：/home/zhang/.local/state/specforge-core/release-checks/v021-recipe-20261029/release.json。

