# 模板UI风格提炼与存量页面差异

当前进度见 [食谱主流程整改结果](UI_RECIPE_ALIGNMENT.md) 和 [通用页面整改结果](UI_GENERIC_ALIGNMENT.md)。以下保留规范提炼阶段的发现，不代表所有问题仍未处理。

2026-10-27，按客户使用过程查看了食谱发现/收藏/详情/发布表单，并对照后台模板用户列表和新增弹窗，结合主题、SCSS及组件源码整理规范。本次不把新增文档当成页面整改已完成。

## 权威说明

传入模板的 docs/template/ui-style.md 为风格规范，ui-reference.md为参考源码索引，ui-ai-checklist.md提供AI任务要求；frontend/AGENTS.md在前端修改时要求读取这些文档。

## 初始确认的偏差（整改前）

| 项目 | 模板基准 | 整改前生成实现 | 处理优先级 |
| --- | --- | --- | --- |
| 内容框架 | 应用容器，boxed1200，pa-4卡片 | RecipePanel另设1280px外壳、RecipeStats另设1100px | 高 |
| 查询区 | outlined/compact网格、搜索/重置 | 食谱默认filled输入、自定义grid、无重置 | 高 |
| 卡片 | 主题surface、全局8px圆角和边框/阴影设置 | 自定义16px圆角、rgba背景/边框及渐变封面 | 高 |
| 标题 | 组件标题和全局字体层级 | 32px/700/字距2px及额外宣传标语 | 中 |
| 编辑 | secondary compact标题栏、outlined表单和响应式两列 | 无统一标题栏、默认filled、裸原生上传控件 | 高 |
| 详情 | 实体v-card表面、统一标题和操作 | 深色窄屏下可见背景文字干扰 | 高；先复现确认后改 |
| 校验 | UserForm/Yup与字段错误回填 | 空表单保存仅出现“请求失败，请稍后重试”，无字段定位 | 高 |
| 确认 | ConfirmDialog/Vuetify | 通用和食谱资产仍有window.confirm | 高 |
| 断点 | useDisplay和Vuetify网格 | 食谱650/1000、统计700的独立断点 | 中 |
| 空态 | 按场景和权限引导 | 无收藏仍提示“记录第一道好菜”，reader无发布权限 | 中 |
| 通用CRUD | v-data-table-server、分页选项、统一表单 | BusinessPanel手写v-table与独立分页、默认输入与600px弹窗 | 高 |

图文卡片本身不是问题，不要求食谱套用管理表格；问题是没有继承同一套视觉原语与交互约定。模板本身个别属性不完全统一，规范优先引用用户管理与UserForm，角色/权限等模块作为补充基准，并明确已有缺陷不是应模仿的规范。

## 后续整改顺序

1. 以食谱发布/编辑弹窗做第一份参考实现：原API、字段、权限和revision合同不变，按UserForm/AddUser统一标题、输入、网格、校验和上传外观。
2. 统一食谱查询、图文卡片、详情和空态，保留合理的业务展示结构。
3. 统一RecipeStats和BusinessPanel，把共用模式归入生成资产。
4. 在同主题同视口下比较浅/深与桌面/手机，再跑发布审核收藏和权限回归。未过的状态留在清单，不能只以原145项API和13步浏览器证明视觉完成。

## 证据与范围

本地截图保存在 openclaw-codegen 的忽略目录 artifacts/admin-platform/customer-review-20261027/：01-recipe-detail.png、02-empty-favorites.png、03-empty-form-error.png、template-user-list.png、template-user-form.png。含本机测试数据，不复制到模板发布仓库。原始截图主题和视口并非完全相同，因此不用于直接比较像素尺寸；具体偏差同时以源码确认，整改复验必须统一条件。

本次没有修改运行中的食谱页、角色权限或模板主题，也没有推送GitHub。客户体验任务转入UI风格整改准备；完整发布/审核客户复核将在整改后继续，不能说本轮又完成了一次完整客户验收。

## 规范复制验证

2026-10-27 使用正式模板本地提交 `28a93f8` 执行独立 generate，运行编号 `20261027T080911-1923722014`。生成副本中的三份 UI 指南和 `frontend/AGENTS.md` 与模板逐字节一致。该项仅证明文档交付，不代表页面视觉达标；未执行构建或发布。证据：本地 `artifacts/admin-platform/customer-review-20261027/ui-guidance-generation.json`。
