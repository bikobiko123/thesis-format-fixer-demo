# Thesis Format Fixer Demo / 毕业论文格式智能修复 Demo

高校毕业论文格式智能修复系统 demo。用户上传 `.docx` 论文后，系统返回修复后的 `.docx`、格式校验报告，以及剩余人工修复清单。

This is a demo Web tool for university thesis formatting repair. Users upload a `.docx` thesis and receive a repaired `.docx`, a format validation report, and a remaining manual-fix checklist.

The MVP favors a runnable, modular slice over complete university-specific formatting coverage.

本 MVP 优先保证项目可运行、模块边界清晰，而不是一次性覆盖所有真实高校格式细则。

## 产品范围 / Product Scope

当前支持范围：

- 一所示例学校：`Demo University`
- 两套培养层次规则：本科、硕士
- 仅支持 `.docx`
- 仅处理论文提交前的格式修复
- 规则引擎负责确定性修复，LLM provider 抽象预留给结构识别解释和错误说明

Currently in scope:

- One demo school: `Demo University`
- Two degree tracks: undergraduate and master
- `.docx` only
- Thesis pre-submission formatting repair only
- Rule-based deterministic repair, with an LLM provider abstraction reserved for structure/error explanations

当前不支持：

- Word 插件
- PDF 处理
- 论文内容生成
- 多学校规则市场
- 承诺修复结果一定通过真实高校最终人工审核

Currently out of scope:

- Word plugins
- PDF processing
- Thesis content generation
- Multi-school rule marketplace
- Legal or administrative guarantees that the repaired document will pass a real university's final office review

## 系统架构 / Architecture

```text
frontend React app
  -> FastAPI /api/process
    -> DOCX engine abstraction
    -> heuristic structure recognizer
    -> thesis IR
    -> rule-based repair planner
    -> python-docx repair executor
    -> validator
    -> report generator
    -> zip result
```

核心后端模块：

- `backend/app/rules`: 本科/硕士 JSON 规则 schema 与加载器。
- `backend/app/docx_engine`: `DocxEngine` 协议和当前 `python-docx` 实现，为后续替换成 Open XML 引擎预留边界。
- `backend/app/ir`: 论文结构与块级中间表示。
- `backend/app/structure`: 启发式结构识别，覆盖摘要、标题层级、正文、参考文献、附录、图表题注、致谢等。
- `backend/app/repair`: 基于规则的确定性格式修复计划生成。
- `backend/app/validation`: 输出 `pass` / `warn` / `fail` 的格式校验结果。
- `backend/app/llm`: LLM provider 抽象。MVP 默认使用离线 rule-based provider，因此无需 API key 也能运行。
- `backend/app/reports`: 面向用户的 JSON、Markdown 和人工修复清单输出。

Key backend modules:

- `backend/app/rules`: JSON schema and rule loading for undergraduate/master tracks.
- `backend/app/docx_engine`: `DocxEngine` protocol plus the current `python-docx` implementation, with a clean boundary for a future Open XML engine.
- `backend/app/ir`: Thesis structure and block-level intermediate representation.
- `backend/app/structure`: Heuristic recognizer for abstracts, heading levels, body, references, appendix, captions, and acknowledgements.
- `backend/app/repair`: Deterministic formatting repair plan generation.
- `backend/app/validation`: `pass` / `warn` / `fail` validation reporting.
- `backend/app/llm`: LLM provider abstraction. The MVP ships an offline rule-based provider so the demo runs without API keys.
- `backend/app/reports`: User-readable JSON, Markdown, and manual-fix outputs.

## 快速开始 / Quick Start

安装后端依赖：

Install backend dependencies:

```bash
python3.12 -m pip install -e '.[dev]'
```

启动后端：

Run the backend:

```bash
uvicorn app.main:app --app-dir backend --reload
```

启动前端：

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

打开 `http://localhost:5173`，上传 `samples/input/demo_thesis.docx`，即可下载生成的 zip 结果包。

Open `http://localhost:5173`, upload `samples/input/demo_thesis.docx`, and download the generated zip result.

## 测试 / Tests

```bash
python3.12 -m pytest backend/tests -q
python3.12 -m ruff check .
cd frontend && npm run build
```

当前测试覆盖规则加载、结构识别、校验输出、API health，以及 DOCX 处理到 zip 结果包的端到端流程。

Current test coverage includes rule loading, structure recognition, validator output, API health, and end-to-end DOCX processing into a result zip.

## 配置 / Configuration

复制 `.env.example` 为 `.env`。

Copy `.env.example` to `.env`.

重要变量：

- `THESIS_ALLOWED_ORIGINS`: 前端 CORS 来源。
- `THESIS_STORAGE_DIR`: 修复文件和报告的输出目录。
- `THESIS_LLM_PROVIDER`: 当前默认值为 `rule_based`。
- `THESIS_LLM_API_KEY`: 为未来云端或本地 LLM 集成预留。

Important variables:

- `THESIS_ALLOWED_ORIGINS`: CORS origins for the frontend.
- `THESIS_STORAGE_DIR`: Output workspace for repaired files and reports.
- `THESIS_LLM_PROVIDER`: Currently defaults to `rule_based`.
- `THESIS_LLM_API_KEY`: Reserved for future cloud or local LLM integrations.

## 样例文件 / Sample Files

- `samples/input/demo_thesis.docx`: 最小 demo 论文输入文件。
- `samples/output/example_format_report.json`: 代表性的校验报告 payload。
- `scripts/create_sample_docx.py`: 重新生成 demo 输入文件。

- `samples/input/demo_thesis.docx`: Minimal demo thesis input.
- `samples/output/example_format_report.json`: Representative validation report payload.
- `scripts/create_sample_docx.py`: Regenerates the demo input.

## 当前能力边界 / Current Capability Boundaries

MVP 当前可以使用 `python-docx` 解析段落、section、页边距、页眉和页脚；构建块级 IR；用启发式规则识别常见论文章节；应用基础页边距、段落样式、页眉页脚修复；并输出校验报告。

The MVP can parse paragraphs, sections, margins, headers, and footers with `python-docx`; build a block-level IR; identify common thesis sections using deterministic heuristics; apply basic margins, paragraph styles, headers, and footers; and produce validation reports.

已知限制：

- `python-docx` 无法完整更新 Word 动态域，例如真正可刷新的目录。
- 分节符和页码重启能力仍然较基础，生产版本应升级到原始 Open XML 处理。
- 当前结构识别器是启发式规则，不是训练好的分类模型。
- 真实学校规则需要基于官方格式指南编码，并配套 fixture 文档测试。
- 当前 LLM provider 是确定性占位实现；生产集成应加入 prompt/version 日志和安全 fallback。

Known limitations:

- `python-docx` cannot fully update Word fields such as a real dynamic table of contents.
- Section-break and page-number restart behavior is basic and should be upgraded with raw Open XML for production.
- The current recognizer is heuristic, not a trained classifier.
- Real school rules should be encoded from official formatting guides and covered with fixture documents.
- The LLM provider is a deterministic placeholder; production integrations should add prompt/version logging and safe fallback behavior.

## 后续方向 / Roadmap

- 增加原始 Open XML 引擎，支持域代码、分节符、页码重启和目录更新。
- 为每条学校规则增加 golden DOCX fixture 测试。
- 增加 LLM-backed 结构识别器，让 LLM 只提出标签和解释，规则仍然是修复权威。
- 为大文档处理增加进度轮询和持久化 job 记录。
- 增加更丰富的 before/after 格式证据报告。

- Add a raw Open XML engine for field codes, section breaks, page-number restarts, and TOC updates.
- Add fixture-based golden DOCX tests for each school rule.
- Add an LLM-backed structure recognizer that only proposes labels and explanations, while rules remain the repair authority.
- Add progress polling and persisted job records for larger documents.
- Add richer report diffs showing before/after formatting evidence.
