# SpecForge 第二业务验证：图书借阅

本轮使用与设备借用相同的核心、模板、命令、前端组件和验证引擎，新增图书借阅规格及独立业务验收包。没有再建一套代码生成器。

## 本轮新增

- `examples/book_lending.yaml`：图书、借阅申请及数量占用规则。
- 通用 `capacity_reference`：由规格指定关联资源、库存字段、申请数量字段和生效状态，不含图书实体名称分支。
- 整数字段 `min`：规格、数据库 CHECK、后端和前端输入控件共同使用。
- 通用资源目录可用量：返回并展示 `<库存字段>_available`，不允许作为输入修改。
- `acceptance_packs/book_lending`：图书 API 与真实浏览器验收，和设备样板分离。
- 抽取共用 HTTP/SQL 夹具、浏览器登录与报告组件，两个业务共用基础设施。

## 业务约定

待审批不占库存，审批通过后按数量占用。归还按整笔申请处理，释放对应数量；不支持分批归还。库存总数与已借出量分开，总数不会因归还而增加。管理员不能把库存改到已借出数量以下，也不能审批自己的申请。未结束申请阻止删除图书，完成记录继续保留。

并发审批与库存修改锁定同一资源行，再检查生效申请数量；状态变更使用条件更新。相同库存字段上的多个数量工作流计入同一占用池。单件互斥与数量模式分开，原设备规格继续兼容。

## 验收结果

| 检查 | 图书借阅 | 设备兼容回归 |
|---|---|---|
| Maven、前端类型检查和生产构建 | 通过 | 通过 |
| 隔离 Compose 启动 | 通过 | 通过 |
| API 检查 | 77 项通过 | 45 项通过 |
| 真实浏览器流程 | 创建图书、申请2本、批准后可用0、归还后恢复2、只读/无权限限制 | 原提交、审批、归还及权限流程通过 |
| 交付包逐文件哈希 | 通过 | 通过 |
| 验收容器与数据卷清理 | 已清理 | 已清理 |

核心单元测试共65项全部通过。另验证了相同数量能力可以生成 warehouse/claim 等不同名称的实体，证明规则没有写死为 book/loan；该测试属于生成层回归，不冒充第三个完整业务。

Wheel 独立目录导入及两个验收包的浏览器资源检查通过。旧运行时和后台模板维护源保持原样，尚未提交 Git。

## 再次运行图书样板

```bash
cd /home/zhang/projects/ai/SpecForge
python3 -m specforge run \
  --workspace /home/zhang/.local/state/specforge-core/book-lending \
  --spec examples/book_lending.yaml \
  --template /mnt/e/Project/Zhang/openclaw-codegen/templates/admin-platform \
  --acceptance-pack book-lending
```

当前机器使用随附 Windows 脚本：

```powershell
./run-specforge-core.ps1 -Spec /home/zhang/projects/ai/SpecForge/examples/book_lending.yaml -Workspace /home/zhang/.local/state/specforge-core/book-lending -AcceptancePack book-lending
```

图书运行编号：`20261024T063426-077e08c954`。
图书交付包 SHA-256：`eb9bd243cda782dae7515f8da194d2c6dcbf18feabad42e22f041855b59410b0`。
设备兼容运行编号：`20261024T063426-683f886cd5`。

完整合同见 docs/CORE_V1.md。当前已经验证两种真实业务，下一步可以据此盘点旧版可迁移资产；自然语言需求、逾期计费、分批归还和旧项目升级不在本轮范围。
