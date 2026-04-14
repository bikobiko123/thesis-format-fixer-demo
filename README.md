# Thesis Format Fixer

<!-- GitHub README files cannot run JavaScript, so the language switch is anchor-based. -->
<p align="center">
  <a href="#zh"><kbd>中文</kbd></a>
  <a href="#en"><kbd>English</kbd></a>
</p>

<a id="zh"></a>

## 高校毕业论文格式智能修复 Agent

Thesis Format Fixer 是一个面向 Codex / Claude Code 等 agent 的 `.docx` 毕业论文格式修复 demo。它不再走 Web 上传演示路线，而是把核心能力封装成 **CLI + Codex skill + Codex plugin + Claude Code command**：agent 接收论文文件路径，调用本地工具，返回修复后的 `.docx`、格式校验报告和剩余人工修复清单。

这个项目的产品判断很明确：论文格式修复更像一个可被 agent 调用的专业工具，而不是一个孤立的网页表单。用户真正需要的是把“识别格式问题 -> 确定性修复 -> 说明剩余人工动作”嵌进自己的写作与提交工作流。

### 当前演示效果

最新一轮使用真实“修改前”论文和理想“修改后”论文反推规则后，`swufe_master` profile 的本地 smoke test 结果为：

| 指标 | 当前结果 |
| --- | --- |
| 校验摘要 | `9 pass / 1 warn / 0 fail` |
| 修复操作 | 页边距、页脚页码域、目录 dirty 标记、页眉、段落样式、分节符 |
| 唯一 warning | 需要在 Word 中更新字段/目录 |
| 内容安全 | 不生成、不改写、不提交真实论文正文 |

这里的边界也必须说清楚：理想修改后文件包含更多前置页、人工分节和已刷新目录等 Word 应用层效果；当前 demo 不会伪造或复制论文内容，也不会在服务器端重新计算完整目录页码。下一步要逼近 1:1 效果，应增加“学校模板模式”和 Word/LibreOffice 字段刷新自动化。

### 它解决什么

- 用户提供 `.docx` 论文。
- 系统解析段落、样式、section、页眉页脚、目录字段和页码字段。
- 结构识别器识别摘要、关键词、标题层级、正文、参考文献、附录、致谢、图表题注。
- LLM 只允许提出结构标签和解释，不能直接决定修复。
- 规则引擎根据学校规则生成确定性修复计划。
- Open XML / python-docx 引擎执行可自动化的格式修复。
- 校验器输出 `pass / warn / fail`。
- 报告模块生成用户可读的 Markdown / JSON 报告和人工修复清单。

### 产品范围

当前支持：

- 一所示例学校规则：西南财经大学硕士论文 `swufe_master`。
- 两套 demo 规则：本科、硕士。
- 仅支持 `.docx`。
- 仅做论文提交前格式修复。
- 优先作为 agent skill / plugin / CLI 使用。
- 提供脱敏真实前后样例，不保留真实论文正文。

当前不做：

- Word 插件。
- PDF 处理。
- 论文内容生成。
- Web 上传界面。
- 多学校规则市场。
- 对真实高校最终人工审核作保证。

### 系统架构

```text
Codex / Claude Code / shell
  -> thesis-fix CLI
    -> DOCX engine abstraction
       -> python-docx parser
       -> raw Open XML repair engine
    -> structure recognizer
       -> heuristic recognizer
       -> optional LLM-backed label helper
    -> thesis IR
    -> rule-based repair planner
    -> validator
    -> report generator
    -> repaired DOCX + reports + zip bundle
```

核心模块：

| 模块 | 职责 |
| --- | --- |
| `backend/app/rules` | 本科、硕士、SWUFE master JSON 规则 schema 与加载器 |
| `backend/app/docx_engine` | DOCX 抽象接口、`python-docx` 解析、Open XML 修复 |
| `backend/app/ir` | 论文结构与块级中间表示 |
| `backend/app/structure` | 启发式结构识别与 LLM-backed 识别装饰器 |
| `backend/app/repair` | 基于规则的确定性修复计划 |
| `backend/app/validation` | `pass / warn / fail` 校验输出 |
| `backend/app/reports` | JSON、Markdown、人工清单和 zip 输出 |
| `skills/thesis-format-fixer` | Codex skill 包装 |
| `plugins/thesis-format-fixer` | repo-local Codex plugin 包装 |
| `.claude/commands/thesis-fix.md` | Claude Code slash command 草案 |

### 快速开始

```bash
python3.12 -m pip install -e '.[dev]'
```

从仓库根目录运行：

```bash
python3.12 -m app.cli repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out ./outputs/thesis-fix \
  --docx-engine openxml \
  --structure-recognizer heuristic
```

也可以使用安装后的脚本入口：

```bash
thesis-fix repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out ./outputs/thesis-fix \
  --docx-engine openxml \
  --structure-recognizer heuristic
```

输出目录会包含：

```text
repaired_thesis.docx
format_report.json
format_report.md
manual_fix_list.md
thesis_format_fix_result.zip
```

### Agent 用法

Codex 使用：

```text
Use the thesis-format-fixer skill to repair this DOCX:
/absolute/path/to/thesis.docx
Profile: swufe_master
Engine: openxml
```

Claude Code 使用：

```text
/thesis-fix /absolute/path/to/thesis.docx
```

LLM-backed 结构识别模式：

```bash
python3.12 -m app.cli repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out ./outputs/thesis-fix-llm \
  --docx-engine openxml \
  --structure-recognizer llm \
  --llm-provider openai_compatible \
  --llm-endpoint "$THESIS_LLM_ENDPOINT" \
  --llm-api-key "$THESIS_LLM_API_KEY" \
  --llm-model "$THESIS_LLM_MODEL"
```

LLM 模式的硬约束：LLM 只能提出标签和解释；规则引擎仍然是修复权威。

### 配置

复制 `.env.example` 为 `.env`，按需设置：

| 变量 | 说明 |
| --- | --- |
| `THESIS_STORAGE_DIR` | 输出目录 |
| `THESIS_DOCX_ENGINE` | `openxml` 或 `python_docx` |
| `THESIS_STRUCTURE_RECOGNIZER` | `heuristic` 或 `llm` |
| `THESIS_LLM_PROVIDER` | 默认 `rule_based`，也支持 `openai_compatible` |
| `THESIS_LLM_ENDPOINT` | OpenAI-compatible endpoint |
| `THESIS_LLM_API_KEY` | LLM API key |
| `THESIS_LLM_MODEL` | LLM model |

### 样例资产

| 路径 | 说明 |
| --- | --- |
| `samples/input/demo_thesis.docx` | 最小 demo 输入 |
| `samples/realistic_swufe/swufe_before_anonymized.docx` | 真实修改前论文的脱敏格式镜像 |
| `samples/realistic_swufe/swufe_after_anonymized.docx` | 真实修改后论文的脱敏格式镜像 |
| `samples/realistic_swufe/format_delta.json` | 前后格式差异摘要 |
| `samples/realistic_swufe/policy_rules_used.json` | 从政策文件整理出的 demo 规则要点 |
| `samples/output/example_format_report.json` | 示例校验报告 |
| `scripts/build_anonymized_real_demo.py` | 从本机真实前后 DOCX 生成脱敏 demo 资产 |

### 测试

```bash
python3.12 -m pytest backend/tests -q
python3.12 -m ruff check .
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/thesis-format-fixer
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/thesis-format-fixer/skills/thesis-format-fixer
```

### 当前能力边界

- Open XML 引擎可以改写 section 属性、页脚 PAGE 域、页码重启和目录 dirty 标记。
- `python-docx` 引擎适合做解析和基础段落样式修复，但不适合处理所有 Word 字段细节。
- 目录可以插入/标记为需要刷新，但目录页码需要 Word 或兼容办公套件刷新。
- 结构识别仍以启发式为主，LLM 只是辅助标签器。
- SWUFE 规则是 demo profile，不等于学校官方系统认证。
- 脱敏样例保留格式形态，不保留真实正文和敏感信息。

### Roadmap

- 增加学校模板模式，插入经过批准的封面、声明、目录骨架等前置页。
- 增加 Word / LibreOffice 自动刷新字段和目录的 runner。
- 为每条学校规则增加 golden DOCX fixture。
- 为 LLM-backed 结构识别增加离线评测集、prompt 版本管理和置信度阈值。
- 输出更直观的 before/after 格式证据报告。
- 把 skill/plugin 打包成更容易安装的 agent 工具包。

<p align="center">
  <a href="#zh"><kbd>回到中文</kbd></a>
  <a href="#en"><kbd>Switch to English</kbd></a>
</p>

---

<a id="en"></a>

## Thesis Formatting Repair Agent

Thesis Format Fixer is a `.docx` university thesis formatting repair demo built for Codex, Claude Code, and similar coding agents. It no longer ships a web upload layer. Instead, the core workflow is packaged as a **CLI + Codex skill + Codex plugin + Claude Code command**: an agent receives a local thesis path, runs the repair tool, and returns a repaired `.docx`, a validation report, and a remaining manual-fix checklist.

The product direction is intentionally agent-first. Thesis formatting repair is more useful as a specialized tool inside a writing and submission workflow than as a standalone web form.

### Current Demo Result

After using a real before/after thesis pair to refine the formatting rules, the latest local smoke test for the `swufe_master` profile reports:

| Metric | Result |
| --- | --- |
| Validation summary | `9 pass / 1 warn / 0 fail` |
| Repairs | Margins, footer page-number fields, TOC dirty marker, header text, paragraph styles, section breaks |
| Only warning | Open the repaired document in Word and update fields/table of contents |
| Content safety | No thesis content generation, rewriting, or committed real body text |

The boundary matters: the ideal after-file includes additional front matter, manual sectioning, and an already refreshed Word table of contents. This demo does not fabricate or copy thesis content, and it does not recalculate full visible TOC page numbers server-side. To get closer to a 1:1 result, the next step is a school-template mode plus Word/LibreOffice field-refresh automation.

### What It Does

- Accepts a `.docx` thesis.
- Parses paragraphs, styles, sections, headers/footers, TOC fields, and page-number fields.
- Recognizes abstracts, keywords, heading levels, body text, references, appendices, acknowledgements, and figure/table captions.
- Allows LLMs to propose labels and explanations only.
- Uses the rule engine as the sole authority for deterministic repair.
- Applies supported repairs through Open XML and `python-docx`.
- Validates rules as `pass / warn / fail`.
- Produces user-readable Markdown / JSON reports and a manual-fix checklist.

### Product Scope

Currently supported:

- One realistic school profile: SWUFE master thesis rules, `swufe_master`.
- Two demo rule tracks: undergraduate and master.
- `.docx` only.
- Pre-submission thesis formatting repair only.
- Agent skill / plugin / CLI usage.
- Anonymized before/after sample assets without real thesis body text.

Out of scope:

- Word plugin.
- PDF processing.
- Thesis content generation.
- Web upload UI.
- Multi-school rule marketplace.
- Guarantees that a real university office will approve the final document.

### Architecture

```text
Codex / Claude Code / shell
  -> thesis-fix CLI
    -> DOCX engine abstraction
       -> python-docx parser
       -> raw Open XML repair engine
    -> structure recognizer
       -> heuristic recognizer
       -> optional LLM-backed label helper
    -> thesis IR
    -> rule-based repair planner
    -> validator
    -> report generator
    -> repaired DOCX + reports + zip bundle
```

Core modules:

| Module | Responsibility |
| --- | --- |
| `backend/app/rules` | Undergraduate, master, and SWUFE master JSON rules and loaders |
| `backend/app/docx_engine` | DOCX interface, `python-docx` parsing, Open XML repair |
| `backend/app/ir` | Thesis structure and block-level intermediate representation |
| `backend/app/structure` | Heuristic recognizer and LLM-backed recognizer decorator |
| `backend/app/repair` | Deterministic rule-based repair planning |
| `backend/app/validation` | `pass / warn / fail` validation output |
| `backend/app/reports` | JSON, Markdown, manual checklist, and zip output |
| `skills/thesis-format-fixer` | Codex skill package |
| `plugins/thesis-format-fixer` | Repo-local Codex plugin package |
| `.claude/commands/thesis-fix.md` | Draft Claude Code slash command |

### Quick Start

```bash
python3.12 -m pip install -e '.[dev]'
```

Run from the repository root:

```bash
python3.12 -m app.cli repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out ./outputs/thesis-fix \
  --docx-engine openxml \
  --structure-recognizer heuristic
```

Or use the installed script:

```bash
thesis-fix repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out ./outputs/thesis-fix \
  --docx-engine openxml \
  --structure-recognizer heuristic
```

The output directory contains:

```text
repaired_thesis.docx
format_report.json
format_report.md
manual_fix_list.md
thesis_format_fix_result.zip
```

### Agent Usage

Codex:

```text
Use the thesis-format-fixer skill to repair this DOCX:
/absolute/path/to/thesis.docx
Profile: swufe_master
Engine: openxml
```

Claude Code:

```text
/thesis-fix /absolute/path/to/thesis.docx
```

LLM-backed structure recognition:

```bash
python3.12 -m app.cli repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out ./outputs/thesis-fix-llm \
  --docx-engine openxml \
  --structure-recognizer llm \
  --llm-provider openai_compatible \
  --llm-endpoint "$THESIS_LLM_ENDPOINT" \
  --llm-api-key "$THESIS_LLM_API_KEY" \
  --llm-model "$THESIS_LLM_MODEL"
```

Hard rule for LLM mode: the LLM only proposes labels and explanations; the rule engine remains the repair authority.

### Configuration

Copy `.env.example` to `.env` and set what you need:

| Variable | Purpose |
| --- | --- |
| `THESIS_STORAGE_DIR` | Output directory |
| `THESIS_DOCX_ENGINE` | `openxml` or `python_docx` |
| `THESIS_STRUCTURE_RECOGNIZER` | `heuristic` or `llm` |
| `THESIS_LLM_PROVIDER` | Defaults to `rule_based`; also supports `openai_compatible` |
| `THESIS_LLM_ENDPOINT` | OpenAI-compatible endpoint |
| `THESIS_LLM_API_KEY` | LLM API key |
| `THESIS_LLM_MODEL` | LLM model |

### Sample Assets

| Path | Description |
| --- | --- |
| `samples/input/demo_thesis.docx` | Minimal demo input |
| `samples/realistic_swufe/swufe_before_anonymized.docx` | Anonymized format mirror of a real before-file |
| `samples/realistic_swufe/swufe_after_anonymized.docx` | Anonymized format mirror of a real after-file |
| `samples/realistic_swufe/format_delta.json` | Before/after formatting delta |
| `samples/realistic_swufe/policy_rules_used.json` | Demo rules derived from the policy document |
| `samples/output/example_format_report.json` | Example validation report |
| `scripts/build_anonymized_real_demo.py` | Builds anonymized demo assets from local real before/after DOCX files |

### Tests

```bash
python3.12 -m pytest backend/tests -q
python3.12 -m ruff check .
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/thesis-format-fixer
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/thesis-format-fixer/skills/thesis-format-fixer
```

### Current Boundaries

- The Open XML engine can rewrite section properties, footer PAGE fields, page-number restarts, and TOC dirty markers.
- The `python-docx` engine is useful for parsing and basic paragraph style repair, but not all Word field details.
- The tool can insert or mark a TOC for refresh, but Word or a compatible office suite must refresh visible TOC page numbers.
- Structure recognition is still heuristic-first; the LLM is only a label helper.
- The SWUFE rules are a demo profile, not an official certification from the university.
- Anonymized samples preserve formatting shape, not real body text or sensitive information.

### Roadmap

- Add school-template mode for approved cover, declaration, and TOC skeleton pages.
- Add Word / LibreOffice runners for automatic field and TOC refresh.
- Add golden DOCX fixtures for each school rule.
- Add offline evaluation, prompt versioning, and confidence thresholds for LLM-backed recognition.
- Generate richer before/after formatting evidence reports.
- Package the skill/plugin as an easier-to-install agent toolkit.

<p align="center">
  <a href="#zh"><kbd>中文</kbd></a>
  <a href="#en"><kbd>English</kbd></a>
</p>
