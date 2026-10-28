# 当前维护与发布状态

当前维护版本为 [v0.2.0](releases/v0.2.0.md)，默认master仅包含新版核心。旧运行时、内置backend、skills和兼容层已经退役；不存在旧入口回退。

本次退役已完成核心97项、外部无副作用检查3项、五套重新生成生产文件一致性以及0.2.0安装包独立安装生成验证。证据见 [退役记录](core-evidence/legacy-retirement.json)，数据保留范围见 [退役说明](LEGACY_RETIRED.md)。

正式版本与附件：[SpecForge v0.2.0](https://github.com/zhdongjie/SpecForge/releases/tag/v0.2.0)。标签发布流程会回下载附件校验并生成release-receipt/v0.2.0，旧标签不覆盖。

v0.1.x是退役前的历史版本，原兼容承诺不适用于当前版本。其 [发布核验](core-evidence/release-published-20261028.json)、[人工客户体验](CUSTOMER_ACCEPTANCE_20261028.md) 及五套完整集成证据保留原日期。后端模板继续使用独立模板仓库的v1.0.4。

旧本地运行数据保存在仓库外私有归档，未上传；新工作区、交付包与数据库未清理。外部旧集成源码已经拒绝执行，但本次不重启飞书消息服务，也不触发任何任务或消息。
