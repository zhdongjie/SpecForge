# C-005 食谱应用合同

- 编号：C-005
- 状态：已验证
- 适用范围：显式 recipe-management 应用；全新项目生成
- 最近验证日期：2026-10-24
- 实现：[应用模块](../../../specforge/applications/recipe_management/__init__.py)
- 证据：[食谱完整验收结果](../../core-evidence/recipe-project.json)

当前食谱规则、字段限制、权限和状态流统一维护在 [食谱项目合同](../../RECIPE_PROJECT.md)。新增权限必须同时约束页面和接口。尤其不能授予原始菜谱实体 CRUD 权限替代应用 API，否则会绕过作者身份、发布审核和明细事务。
