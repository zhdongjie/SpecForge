# SpecForge core v1 操作入口

新项目使用独立 `specforge` 包；旧运行时冻结兼容。当前已验证设备借用、图书借阅及显式食谱应用。样板历史见 [第二业务验收](CORE_V1_SECOND_BUSINESS.md)，真实应用见 [食谱项目](RECIPE_PROJECT.md)。当前规则以 [工程知识库](knowledge/README.md) 为准。

## 安装与运行

需要 Python 3.10+、JDK 17、Maven 3.9+、模板锁定版本的 Node/pnpm、Docker Compose 和 Chromium。工具加入 PATH。

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests_core -v
python3 -m unittest discover -s tests_compat -v
python3 -m specforge run --workspace /absolute/workspace/device-borrow --spec examples/device_borrow.yaml --template /absolute/path/to/admin-platform --acceptance-pack device-borrow
```

图书借阅使用 `examples/book_lending.yaml`、独立 workspace 和 `--acceptance-pack book-lending`。其他命令见 `python3 -m specforge --help`。`verify --build-only` 仅诊断构建，不能发布；`verify --reuse-build` 要求源码及产物仍匹配，会重新进行完整业务验收。

纯 Linux 浏览器依赖安装：`pip install -e ".[acceptance]"`，然后 `python -m playwright install chromium` 并安装浏览器系统依赖。

## Browser adapter for Windows/WSL

There is one JavaScript browser scenario per acceptance pack. The portable default uses the Node runtime and Playwright core bundled with the optional Python Playwright distribution; Python contains no duplicate UI workflow. An optional Windows Node adapter can reuse a locally installed Playwright and Chromium without downloading a second browser into WSL:

```bash
export SPECFORGE_BROWSER_NODE=/mnt/c/path/to/node.exe
export SPECFORGE_PLAYWRIGHT_MODULE=C:/path/to/node_modules/playwright
export SPECFORGE_CHROMIUM_EXECUTABLE='C:/Program Files/Google/Chrome/Application/chrome.exe'
```

Credentials pass via stdin, never command-line arguments. The adapter stages its script and screenshots on a Windows native temporary drive, then copies only browser reports/screenshots back into the WSL run. Credentials are not retained in handoff reports. For hosts whose long-running WSL sessions lose Windows interop access, use `tools/run-core-windows.ps1`: it starts a hidden native worker, executes the full CLI, and cleans its private staging directory. Its Node, Playwright module, browser, distribution, template, spec and workspace paths are configurable. `-ReuseBuild` retries full acceptance without rebuilding matching artifacts.


## 排错与合同

先读 `reports/verify.json` 的 failed_stage，再看对应构建、API 或浏览器报告。未知错误停止，不扩大自动修复范围。

- [规格](knowledge/contracts/specification.md)
- [模板扩展](knowledge/contracts/template.md)
- [工作区与交付](knowledge/contracts/workspace-release.md)
- [验证和修复](knowledge/contracts/verification-repair.md)
- [旧资产兼容与历史测试](LEGACY_MIGRATION.md)


## 固定字段变更验收

`examples/book_fields_v1.yaml` 新增可选 ISBN 和带 min/default 的书架号；`examples/book_fields_v2.yaml` 将 ISBN 改名为馆藏编号，删除书架号并修改名称标签。两者使用全新数据库，不是存量升级脚本。

```bash
python3 -m specforge run --workspace /absolute/workspace/book-fields-v1 --spec examples/book_fields_v1.yaml --template /absolute/path/to/admin-platform --acceptance-pack book-lending-fields
python3 -m specforge run --workspace /absolute/workspace/book-fields-v2 --spec examples/book_fields_v2.yaml --template /absolute/path/to/admin-platform --acceptance-pack book-lending-fields
```

验收包通过固定 project.id `book_fields_v1` / `book_fields_v2` 显式选择场景，再严格校验对应字段合同；不是根据字段名推断场景。复用原图书借阅 API 全集和同一个浏览器脚本，增加字段断言。证据见 [字段变更验收](core-evidence/field-changes.json)。


## 交付包独立部署验收

这是开发验收工具，应用部署只需要包内生产产物和 Docker，不依赖本仓库。

```bash
python3 tools/verify-release.py --archive /absolute/release.zip --reports /absolute/new-report-directory --acceptance-pack book-lending
```

校验和文件默认在交付包旁的 `.zip.sha256`。报告目录必须尚不存在，避免覆盖证据。工具校验整个包及文件清单，解压至全新临时目录，以独立 Compose 项目和全新卷启动包内 JAR / dist，执行完整 API 和浏览器验收，最后清理。允许缓存或下载固定摘要的 Docker 基础镜像；不承诺离线部署。

Windows / WSL 浏览器工作进程包装：

```powershell
./run-core-windows.ps1 -ReleaseArchive /absolute/release.zip -ReportsDirectory /absolute/new-report-directory -AcceptancePack book-lending
```

`release.json` 是独立交付验收结论；`mounts.json` 记录实际挂载，API / 浏览器报告与脱敏诊断位于同一目录。此验收不更改原生成记录及 published.json。失败不能视为最终交付完成；清理失败也会报告 FAIL。验收临时账号不属于正式部署配置，实际安装按包内文档设置管理员环境变量。
