# SpecForge core v1 操作入口

新项目使用独立 `specforge` 包；旧运行时冻结兼容。当前已验证设备借用和图书借阅两套完整业务，详见 [历史验收证据](CORE_V1_SECOND_BUSINESS.md)。当前规则以 [工程知识库](knowledge/README.md) 为准。

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
