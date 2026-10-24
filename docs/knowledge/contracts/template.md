# C-002 模板扩展合同

- 编号：C-002
- 状态：已采用；环境根因未确认的部分在正文标注
- 适用范围：SpecForge core 0.1.0；重新生成全新项目
- 最近验证日期：2026-10-24
- 实现：[specforge/generate.py](../../../specforge/generate.py)
- 证据：[第二业务验收](../../core-evidence/second-business.json)

模板路径由调用者显式提供。本机使用外部 admin-platform 模板。复用 com.original 包、统一响应、认证、权限、分页和动态路由；仅在生成副本中增加业务扩展和 SQL，模板源目录保持不变。私有环境、密钥、运行数据与构建缓存不进入副本。


食谱应用在生成副本中设置模板显式 `frontend/src/appConfig.ts` 品牌名称，并增加专用业务 API 和页面。原模板认证、权限基础设施和源模板文件不改动。
