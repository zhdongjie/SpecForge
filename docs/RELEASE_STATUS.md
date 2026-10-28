# 发布状态

> v0.1.x发布历史。当前旧方案已退役，默认分支仅维护新版，见 [退役说明](LEGACY_RETIRED.md)。

2026-10-28。正式发布并核实：

- [SpecForge v0.1.1](https://github.com/zhdongjie/SpecForge/releases/tag/v0.1.1)：核心wheel、源码zip、SHA256SUMS。
- [后台模板 v1.0.4](https://github.com/zhdongjie/springboot3-vue3-vuetify-admin-template/releases/tag/v1.0.4)：源码zip、SHA256SUMS，含UI复用规范。

仓库内置发布流程已回下载附件并通过校验；回执标签分别为release-receipt/v0.1.1、release-receipt/v1.0.4。本机按正式标签、UTC归档元数据重建源码zip，与线上回执的SHA256逐字一致。详见 [发布证据](core-evidence/release-published-20261028.json)。

核心维护分支为codex/core-v0.1，旧master保留原状；获取新版请使用正式标签或该维护分支。初始v0.1.0/v1.0.3标签保留，新补丁完善受限仓库检出和附件验收，没有覆盖旧标签。

人工客户体验见 [验收记录](CUSTOMER_ACCEPTANCE_20261028.md)。完成作者/审核/收藏/只读权限/统计等实际流程；保留一份验收草稿，原公开数量与收藏数量恢复。无真实邮件、密码改动、角色扩权或数据库重建。非阻断体验改进CX-001/002/003继续保留，不宣称已修复。

本次核心代码与五套系统验收版本相同；正式打包新增全新环境安装及真实生成验证，97项核心和9项兼容通过，最终模板生成445个生产文件与已集成验收源码一致。原完整集成报告保持2026-10-27日期。

源码和发布附件不含本地数据库、完整环境文件、测试凭据、截图或原始运行日志。发布只使用Git正常认证及仓库内置授权；本地保存凭据的提取操作未执行。
