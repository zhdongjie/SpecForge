# T-001 事务与 JDBC 行锁

- 编号：T-001
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/assets/BusinessResource.java](../../../specforge/assets/BusinessResource.java)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

现象：原注解事务未实现预期的 JDBC 锁互斥。根因：必须保证 JdbcTemplate 与事务管理器绑定同一数据源。处理：使用显式 DataSourceTransactionManager 和 TransactionTemplate，统一资源行锁顺序。验证：设备并发审批、图书超量竞争和重复归还 API 检查。


本条原验证针对纯 JDBC 借用模块。复用 MyBatis-Flex 服务时不能直接推广；混合事务须按 [T-006](mixed-transactions.md) 适配并用写入后故障注入证明共同回滚。

2026-10-29的文件生命周期共用协议已在模板验证：清理使用独立READ_COMMITTED事务以避免空引用间隙锁影响其他文件；这不是把全部业务事务改成该隔离级别。引用与业务主记录仍要加入同一业务事务。真实竞争与调用约束见[第二轮复用](../../FILE_LIFECYCLE_REUSE.md)。
