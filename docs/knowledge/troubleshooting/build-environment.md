# T-004 本机容器构建环境

- 编号：T-004
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[tools/run-core-windows.ps1](../../../tools/run-core-windows.ps1)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

现象：当前宿主 BuildKit 获取镜像元数据长时间等待。根因：已确认卡在注册表元数据阶段，网络侧根因尚待验证。处理：本机使用已有固定摘要镜像及 DOCKER_BUILDKIT=0 的传统构建器完成验证。验证：已有 Compose 启动检查通过。此项是环境规避措施，不应修改模板业务规则，也不能据此承诺离线部署。
