# T-002 初始化 SQL 中文乱码

- 编号：T-002
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/generate.py](../../../specforge/generate.py)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

现象：业务权限和标签中文乱码。根因：模板 SQL 调整过字符集，追加内容继承了不合适的连接字符集。处理：生成业务 SQL 前明确 SET NAMES utf8mb4。验证：初始化后 API 与真实浏览器显示中文标签。
