# D-004 显式独立验收包

- 编号：D-004
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/acceptance_packs/__init__.py](../../../specforge/acceptance_packs/__init__.py)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

问题：通用验证器容易混入领域猜测和重复流程。采用方案：验收包拥有业务夹具与断言，共享 HTTP、SQL、浏览器登录和报告设施；调用者显式选择验收包。代价：新增领域须补验收案例。重新评估条件：跨业务断言重复时提取有证据的共性，不自动按字段名选择业务。
