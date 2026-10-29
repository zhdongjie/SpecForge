# SpecForge core v1 操作入口

新项目使用独立 `specforge` 包；旧运行时已退役，当前仅保留新核心。当前已验证设备借用、图书借阅及显式食谱应用。样板历史见 [第二业务验收](CORE_V1_SECOND_BUSINESS.md)，真实应用见 [食谱项目](RECIPE_PROJECT.md)。当前规则以 [工程知识库](knowledge/README.md) 为准。

## 安装与运行

需要 Python 3.10+、JDK 17、Maven 3.9+、模板锁定版本的 Node/pnpm、Docker Compose 和 Chromium。工具加入 PATH。

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests_core -v
python3 -m specforge run --workspace /absolute/workspace/device-borrow --spec examples/device_borrow.yaml --template /absolute/path/to/admin-platform --acceptance-pack device-borrow
```

图书借阅使用 `examples/book_lending.yaml`、独立 workspace 和 `--acceptance-pack book-lending`。其他命令见 `python3 -m specforge --help`。`verify --build-only` 仅诊断构建，不能发布；`verify --reuse-build` 要求源码及产物仍匹配，会重新进行完整业务验收。

纯 Linux 浏览器依赖安装：`pip install -e ".[acceptance]"`，然后 `python -m playwright install chromium` 并安装浏览器系统依赖。

## 本机正式模板与直接运行

当前 Windows/WSL 包装入口默认模板为：

```text
/mnt/e/Project/Zhang/openclaw-codegen/exports/github/springboot3-vue3-vuetify-admin-template
```

这是模板独立仓库的本地工作副本；修改后应先验证和提交，再生成交付项目。`templates/admin-platform` 是旧的验证/兼容副本，不再作为包装入口默认值。核心CLI仍要求显式 `--template`，其他机器或模板使用 `-Template` 覆盖，不依赖本机目录布局。

Windows PowerShell直接运行，不需要另存可能过期的脚本副本：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& "\\wsl.localhost\Ubuntu\home\zhang\projects\ai\SpecForge\tools\run-core-windows.ps1" `
  -Spec /home/zhang/projects/ai/SpecForge/examples/recipe_management.yaml `
  -Workspace /home/zhang/.local/state/specforge-core/recipe-management `
  -AcceptancePack recipe-management
```

图书/设备仍显式选相应Spec和AcceptancePack，使用各自工作区。每次生成创建新的运行目录；失败不会替换旧成功包。新业务先建立需求和复用审查，不能仅改验收包名字冒充新领域支持。

完成后在工作区的 `published.json` 查看最新通过验收的包路径，在 `runs/<run-id>/reports/` 查看检查及需求覆盖证据。独立部署验收使用下方ReleaseArchive参数，其ReportsDirectory必须是新目录。

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
- [旧方案已退役](LEGACY_RETIRED.md)


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


## 新项目需求覆盖门禁

新项目完整验收和发布必须有生成源码中的 `specforge/requirements.yaml`；四个固定历史样板保留兼容例外。`reports/requirements.json` 给出逐项验证，清单随源码和哈希进入交付包，独立部署再检查。完整流程与项目补充实现方式见 [实施流程](GENERATION_WORKFLOW.md)。不能把生成器已支持的功能当成用户需求边界。


## 独立项目的外部验收包

该入口属于本轮源码改动；历史v0.2.1发布wheel尚未包含它，需使用包含本轮提交的核心。

使用`--acceptance-pack python:your_project.acceptance`显式加载已安装或位于PYTHONPATH的开发验收模块。模块必须提供`validate_spec(spec)`、`accept(origin,password,compose_project,source,reports)`以及同目录browser.cjs（或显式BROWSER_SCRIPT）。接口与内置验收包相同，沿用隔离部署、浏览器和需求覆盖门禁；独立交付验收工具接受相同参数。

该参数加载受信任的Python代码，必须由操作者显式指定；业务YAML不能选择模块或自动执行代码。不会按字段名猜测业务，不将每个真实项目加入核心PACKS。模块仅属于开发验收环境，应用部署不需要安装它。项目定制仍在generate之后应用到副本，verify和package会验证最终副本，重新生成需显式重放本项目定制。
