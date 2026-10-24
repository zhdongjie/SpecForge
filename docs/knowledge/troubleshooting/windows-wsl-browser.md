# T-003 Windows 与 WSL 浏览器运行

- 编号：T-003
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[tools/run-core-windows.ps1](../../../tools/run-core-windows.ps1)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

现象：长时间 WSL 子进程中 Windows 互操作失败，或 Windows 无法读取 WSL UNC 路径。根因：当前宿主环境的互操作与路径边界。处理：Windows 先启动隐藏浏览器工作进程，脚本暂存于 Windows 原生临时盘；仅报告与截图复制回 WSL。验证：现有两个业务的真实浏览器验收。适用范围限定当前 Windows/WSL 环境，不宣称所有宿主均存在此问题。
