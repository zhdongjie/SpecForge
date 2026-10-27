# T-007 上传能力存在不代表初始化策略可直接使用

- 编号：T-007
- 状态：旧模板已适配；当前发布模板源已修复
- 适用范围：admin-platform 旧模板兼容与已修复发布模板的 PNG/JPEG 初始化元数据
- 最近验证日期：2026-10-27
- 实现：[生成副本适配](../../../specforge/applications/recipe_management/__init__.py)
- 证据：[真实 multipart 验收](../../../specforge/acceptance_packs/recipe_management/media.py)、[发布模板回归](../../core-evidence/template-release-regression.json)

2026-10-24 的旧模板有 FileManager、Tika 内容识别、文件类型 / 大小策略和 system_file 表，但初始 MIME 值为 application/png 与 application/jpeg，实际识别值为 image/png 与 image/jpeg。2026-10-27 发布模板本地提交 `8a5e9cf` 已在初始化 SQL 中修正为标准 MIME，并使上传地址使用部署入口；端到端生成和独立部署均通过。这是历史问题，不能再描述成当前模板仍有该缺陷。

适配在生成副本的初始化 SQL 中修正这两条策略数据，不绕过 FileManager，也不修改源模板。前端使用 multipart 上传，后端复用 FileManager；食谱额外限制真实图片及尺寸。返回地址转换为同源 /api/files 路径，文件引用仍保存模板要求的相对路径，避免部署地址或端口变化破坏引用。

完整复用审查必须包括配置与数据，不能只凭看到上传接口就认定接入完成，也不能因为需要适配就删掉上传需求。


复用时还必须检查访问模型：当前模板文件 URL 是静态资源访问。上传权限、业务引用归属、正文权限与私有文件下载授权是不同问题；本次不把静态资源机制描述成私有附件方案。
