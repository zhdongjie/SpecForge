# C-007 生成页面的UI一致性

- 编号：C-007
- 状态：食谱主流程已整改；通用 CRUD 待整改，暂无自动视觉门禁
- 适用范围：新版通用页面和显式应用前端
- 最近验证日期：2026-10-27
- 实现：传入模板的 frontend/AGENTS.md、docs/template/ui-style.md、ui-reference.md、ui-ai-checklist.md
- 证据：[风格差异与整改清单](../../UI_STYLE_ALIGNMENT.md)

UI风格权威在模板中，不在SpecForge另维护一套配色和组件库。生成前选择真实基准页，记录布局、组件属性、主题token与业务结构差异。原有通用BusinessPanel、RecipePanel、RecipeStats不能作为风格符合性的证明。

UI一致性与功能验收分开。API和浏览器步骤通过只证明相应操作，不证明页面与模板风格统一。视觉比对必须固定主题、视口、导航和内容宽度，覆盖表单、详情、空态及错误态，记录未通过项。

食谱主流程已有 [参考实现与验收记录](../../UI_RECIPE_ALIGNMENT.md)，覆盖发布/编辑、图文列表、详情、审核与统计资产。通用 BusinessPanel 仍待迁移。当前未增加自动截图相似度或视觉发布门禁，不能将食谱验收结果推及未修改页面。
