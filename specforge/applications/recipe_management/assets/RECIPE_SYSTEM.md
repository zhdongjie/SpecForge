# 食谱管理系统安装与使用

本包包含后端 JAR、前端 dist、源码、初始化 SQL 和 Docker 部署文件。部署应用不需要 SpecForge，也不需要重新运行 Maven 或 pnpm。Docker 基础镜像需要可下载或已缓存。

## 首次安装

在本文件所在的 admin-platform 目录中执行：

```bash
cp .env.example .env
# 编辑 .env 后再启动
# Docker Compose 项目名自行选择，避免复用其他系统的数据卷
 docker compose -p recipe-kitchen --env-file .env -f deploy/compose.yaml up -d --build --wait
```

必须设置独立数据库、Redis 密码、APP_HTTP_PORT、APP_PUBLIC_URL，并显式开启 APP_BOOTSTRAP_ENABLED=true，设置 APP_BOOTSTRAP_USERNAME 和 APP_BOOTSTRAP_PASSWORD。首次管理员账号为 2–8 字符；密码须为 8–16 位英文字母和数字，包含大小写字母及数字。不要使用验收账号或沿用其他平台数据库。

默认监听本机回环地址。浏览器打开 http://127.0.0.1:配置端口/authorize/login，登录后进入“业务管理 → 食谱厨房”。如果对外提供访问，按实际域名配置 APP_PUBLIC_URL 与反向代理。第一次初始化成功后，可关闭 APP_BOOTSTRAP_ENABLED；不要删除数据库卷。

## 使用方式

管理员通过账号管理创建普通用户并分配 normal 角色，也可使用模板提供的注册入口。普通用户可发现、搜索、收藏、创建和编辑自己的菜谱。管理员可管理分类、审核他人的提交和查看食谱统计；管理员自己的菜谱必须由另一个管理员审核。

保存后为草稿，提交后待审核。待审核不能编辑或删除；驳回显示原因。已发布菜谱编辑后退出公开展示，需重新审核。收藏在撤回期间隐藏，重新发布后恢复。所有编辑和审核都检查修订号，旧页面操作失败时刷新后重试。

食材与步骤为明细；每项食材名称和用量最多 80 字符，每步最多 255 字符，每份菜谱最多 40 项食材和 40 步。封面支持真实 PNG/JPEG 上传（最多 5MB，尺寸不超过 4096×4096），也可选填 HTTPS 图片地址。系统图片必须由当前作者上传，保存、替换、移除和删除会维护平台引用。上传后取消的图片由平台未引用文件清理机制按保留期清理。本版不提供评论或推荐算法。

## 维护

本包面向全新数据库安装，不能把初始化 SQL 直接应用到已有业务库升级。持久化数据包括 database、redis-data、signing-keys 和 uploads 卷；备份与恢复见模板 README。不要执行带 --volumes 的停止命令，除非明确要删除该系统数据。

验收中的临时账号和示例菜谱不包含在交付包内；首次正式部署仅初始化平台基础配置和四个菜谱分类。

交付包包含 `specforge/requirements.yaml` 需求覆盖清单与 `specforge/adaptations/` 模板适配补丁；它们用于追溯复用决定和验证范围，不是要求模板预先支持所有业务。
