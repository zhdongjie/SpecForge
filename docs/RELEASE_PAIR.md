# 固定版本配套与使用

2026-10-30，发行配套：SpecForge v0.3.0 + admin-platform模板v1.1.0。精确模板提交见[配套清单](../template-compatibility.json)。这份清单用于复现输入，不新增运行时自动下载或模板猜测。

1. 从SpecForge的v0.3.0发布页下载wheel、源码ZIP和SHA256SUMS，校验附件。wheel是Python包，源码ZIP提供examples、tools、docs。
2. 从模板v1.1.0发布页下载源码ZIP与SHA256SUMS并校验，解压到独立目录；模板源码包没有生产JAR/dist，需要生成后构建。
3. 在Python>=3.10的虚拟环境安装wheel（会安装PyYAML依赖）。运行核心测试/业务验收还需README所列工具，wheel安装并不自带JDK、Maven、Docker或浏览器。
4. 读取显式模板的docs/template和frontend/AGENTS.md，填写项目需求/复用清单。工作区使用源码外目录。
5. 从源码ZIP的examples选择明确规格；简单样板可run，真实项目按GENERATION_WORKFLOW.md分阶段生成、项目重放、显式验收、打包与独立部署。

示例（替换绝对路径，Linux/WSL浏览器配置见CORE_V1.md）：

```bash
python3 -m venv /absolute/venvs/specforge
/absolute/venvs/specforge/bin/pip install /absolute/downloads/specforge_core-0.3.0-py3-none-any.whl
/absolute/venvs/specforge/bin/python -m specforge run \
  --workspace /absolute/runs/device \
  --spec /absolute/SpecForge-v0.3.0/examples/device_borrow.yaml \
  --template /absolute/admin-platform-v1.1.0 \
  --acceptance-pack device-borrow
```

不要从持续变化的master/main替代固定发行输入后仍声称是同一版本。生成身份以业务规格、模板源码清单和哈希为准。源码ZIP和可部署业务ZIP不是同一种产物；后者通过验收后才生成，包含JAR/dist/SQL和部署配置。

已有交付包不在本次发行中升级或迁移；设备、图书、食谱以及私有工单/本地会议室的历史报告按各自输入身份保留。新应用仍须专属验收。此次不发布工单、会议室源码或业务数据到公共发行页。
