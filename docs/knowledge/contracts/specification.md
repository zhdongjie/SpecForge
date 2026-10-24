# C-001 版本 1 业务规格

- 编号：C-001
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/spec.py](../../../specforge/spec.py)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

字段仅支持 string、integer、boolean、datetime、enum、foreign；未知键、无效引用、非法状态和不支持操作在生成前拒绝。实体与字段命名为小写 snake_case。内部字段禁止覆盖。整数字段 min 与默认值必须满足规格约束。列表和表单显式列出字段。规格字段变更仅适用于重新生成的新项目，不提供存量数据库升级。


固定字段变更回归见 [场景测试](../../../tests_core/test_field_changes.py) 与 [真实验收证据](../../core-evidence/field-changes.json)。两个变体分别以明确项目标识选择场景，均重新生成到独立工作区。增加、改名、删除以及标签修改同步作用于 SQL、后端输入、前端类型和页面；不处理原项目数据迁移。


规格可显式声明 `application`，当前支持 `recipe-management`。未知扩展或不符合其固定实体合同的规格在写入前拒绝；未声明时沿用通用规格路径。具体规则见 [C-005](recipes.md)。
