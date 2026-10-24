# T-006 JDBC 与模板 MyBatis 引用服务必须共同回滚

- 编号：T-006
- 状态：已验证
- 适用范围：当前 admin-platform / MyBatis-Flex 1.10.9，混合 JDBC 与模板服务调用
- 最近验证日期：2026-10-24
- 实现：[食谱事务适配](../../../specforge/applications/recipe_management/assets/RecipeResource.java)
- 证据：[故障注入验收](../../../specforge/acceptance_packs/recipe_management/media.py)

现象：强制新文件引用写入失败后，菜谱主记录恢复了，但旧引用已被删除。只验证校验前失败不能发现这种部分提交。

根因：纯 JDBC 的显式 DataSourceTransactionManager 没有建立 MyBatis-Flex 的事务上下文；复用的 FileReferenceService 使用 FlexSpringTransaction，不能假定它会加入 JDBC 事务。

处理：食谱 JDBC 使用 SqlSessionFactory 的实际数据源，事务模板使用平台 TransactionManagementConfigurer 提供的事务管理器，确保 JDBC 和引用服务共用同一事务连接。清理任务也使用同一平台数据源，在文件行锁后重新检查引用，避免候选过期导致误删。

验证：隔离数据库中用临时触发器令文件引用 INSERT 失败，检查主记录、修订号、旧引用和新引用共同回滚，随后删除触发器。执行真实清理任务，验证已引用文件保留、最后引用释放后可清理。不是只检查代码里有没有事务注解。

纯 JDBC 借用模块的原事务方案保持不变，本条不要求重写平台全局事务配置。


实际故障注入与独立部署证据见 [本轮结果](../../core-evidence/recipe-reuse-fix.json)。清理与食谱关联遵守相同文件锁协议；不据此宣称未适配的其他业务调用方也具有相同并发保证。
