# D-003 单件互斥与数量占用

- 编号：D-003
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/assets/BusinessResource.java](../../../specforge/assets/BusinessResource.java)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

问题：并发批准可能重复借出。采用方案：同一数据源的显式事务，先锁资源行，再检查请求状态并条件更新；单件增加数据库唯一约束，数量模式对生效申请求和。归还改变状态，不累加可变库存。代价：同资源写入串行化，列表可用量是信息快照。重新评估条件：出现高竞争性能瓶颈或部分归还业务时。
