# SpecForge 工程知识库

随源码版本管理的中文文档；不参与生成运行时。规则由代码与测试执行，本文档解释合同、决策与已确认的解法。历史报告仅作为证据，不作为当前合同。

- [C-001 版本 1 业务规格](contracts/specification.md)
- [C-002 模板扩展合同](contracts/template.md)
- [C-003 工作区与交付](contracts/workspace-release.md)
- [C-004 验证与修复边界](contracts/verification-repair.md)
- [D-001 明确规格替代关键词猜测](decisions/explicit-spec.md)
- [D-002 复用模板基础设施](decisions/template-reuse.md)
- [D-003 单件互斥与数量占用](decisions/allocation.md)
- [D-004 显式独立验收包](decisions/acceptance-packs.md)
- [T-001 事务与 JDBC 行锁](troubleshooting/jdbc-lock.md)
- [T-002 初始化 SQL 中文乱码](troubleshooting/sql-charset.md)
- [T-003 Windows 与 WSL 浏览器运行](troubleshooting/windows-wsl-browser.md)
- [T-004 本机容器构建环境](troubleshooting/build-environment.md)

- [T-005 临时管理员密码必须满足模板合同](troubleshooting/bootstrap-password.md)

- [C-005 食谱应用合同](contracts/recipes.md)
- [D-005 显式应用扩展](decisions/application-extensions.md)

- [C-006 需求覆盖与模板复用合同](contracts/delivery-coverage.md)
- [T-006 混合事务回滚](troubleshooting/mixed-transactions.md)
- [T-007 上传 MIME 策略适配](troubleshooting/upload-mime.md)

## 维护方式

先判断知识归属，再更新对应条目。合同是当前规则唯一说明；决策记录问题、方案、代价与重新评估条件；排错记录现象、根因、处理与验证。新条目沿用分类编号，包含状态、适用范围、最近验证日期、代码与证据链接。未经证实的推测标为待验证。

任务完成前检查相关记录是否需要更新；没有可复用知识则不强制增加文章。日志和历史过程留在运行报告，知识库不保存凭据、完整环境文件或原始日志。失效方案标为已替代并链接新条目，不静默删除历史理由。向量检索留待系统成熟后再引入。
