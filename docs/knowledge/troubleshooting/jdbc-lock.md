# T-001 事务与 JDBC 行锁

- 编号：T-001
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/assets/BusinessResource.java](../../../specforge/assets/BusinessResource.java)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

现象：原注解事务未实现预期的 JDBC 锁互斥。根因：必须保证 JdbcTemplate 与事务管理器绑定同一数据源。处理：使用显式 DataSourceTransactionManager 和 TransactionTemplate，统一资源行锁顺序。验证：设备并发审批、图书超量竞争和重复归还 API 检查。
