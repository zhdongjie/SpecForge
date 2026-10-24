# C-004 验证与修复边界

- 编号：C-004
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/verification.py](../../../specforge/verification.py)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

验证阶段区分 preflight、backend、install、frontend、compose、api、browser、cleanup。完整验收必须显式选择兼容验收包。临时环境使用独立项目名、数据卷、凭据和回环地址，不发送真实邮件。仅后端编译失败可进入有回归测试的确定性修复，最多两轮；未知错误停止，认证权限基础设施不自动修改。
