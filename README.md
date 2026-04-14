# Thesis Format Fixer Demo / 毕业论文格式智能修复 Demo

高校毕业论文格式智能修复系统 demo。用户上传 `.docx` 论文后，系统返回修复后的 `.docx`、格式校验报告，以及剩余人工修复清单。

This is a demo Web tool for university thesis formatting repair. Users upload a `.docx` thesis and receive a repaired `.docx`, a format validation report, and a remaining manual-fix checklist.

The MVP favors a runnable, modular slice over complete university-specific formatting coverage.

本 MVP 优先保证项目可运行、模块边界清晰，而不是一次性覆盖所有真实高校格式细则。

## 产品范围 / Product Scope

当前支持范围：

- 一所示例学校：`Demo University`
- 一个真实规则 demo profile：`西南财经大学` 硕士论文格式规则
- 两套培养层次规则：本科、硕士
- 仅支持 `.docx`
- 仅处理论文提交前的格式修复
- 规则引擎负责确定性修复，LLM provider 抽象预留给结构识别解释和错误说明

Currently in scope:

- One demo school: `Demo University`
- One realistic rule demo profile: `Southwestern University of Finance and Economics` master thesis formatting
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
- `backend/app/docx_engine/openxml.py`: 原始 Open XML 修复引擎，支持页边距、页眉页脚距离、页脚页码域、页码重启、分节符和目录 dirty 标记。
- `backend/app/ir`: 论文结构与块级中间表示。
- `backend/app/structure`: 启发式结构识别，覆盖摘要、标题层级、正文、参考文献、附录、图表题注、致谢等。
- `backend/app/structure/llm_recognizer.py`: LLM-backed 结构识别装饰器，只接收标签和解释，不生成修复操作。
- `backend/app/repair`: 基于规则的确定性格式修复计划生成。
- `backend/app/validation`: 输出 `pass` / `warn` / `fail` 的格式校验结果。
- `backend/app/llm`: LLM provider 抽象。MVP 默认使用离线 rule-based provider，因此无需 API key 也能运行。
- `backend/app/reports`: 面向用户的 JSON、Markdown 和人工修复清单输出。

Key backend modules:

- `backend/app/rules`: JSON schema and rule loading for undergraduate/master tracks.
- `backend/app/docx_engine`: `DocxEngine` protocol plus the current `python-docx` implementation, with a clean boundary for a future Open XML engine.
- `backend/app/docx_engine/openxml.py`: Raw Open XML repair engine for margins, header/footer distances, footer page-number fields, page-number restarts, section breaks, and TOC dirty marking.
- `backend/app/ir`: Thesis structure and block-level intermediate representation.
- `backend/app/structure`: Heuristic recognizer for abstracts, heading levels, body, references, appendix, captions, and acknowledgements.
- `backend/app/structure/llm_recognizer.py`: LLM-backed structure recognizer decorator that only accepts labels and explanations, never repair operations.
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
- `THESIS_DOCX_ENGINE`: DOCX 引擎，支持 `openxml` 和 `python_docx`。
- `THESIS_STRUCTURE_RECOGNIZER`: 结构识别器，支持 `heuristic` 和 `llm`。
- `THESIS_LLM_PROVIDER`: 当前默认值为 `rule_based`。
- `THESIS_LLM_PROVIDER=openai_compatible`: 启用 OpenAI-compatible JSON LLM provider。
- `THESIS_LLM_ENDPOINT` / `THESIS_LLM_API_KEY` / `THESIS_LLM_MODEL`: LLM-backed 结构识别配置。

Important variables:

- `THESIS_ALLOWED_ORIGINS`: CORS origins for the frontend.
- `THESIS_STORAGE_DIR`: Output workspace for repaired files and reports.
- `THESIS_DOCX_ENGINE`: DOCX engine, supports `openxml` and `python_docx`.
- `THESIS_STRUCTURE_RECOGNIZER`: Structure recognizer, supports `heuristic` and `llm`.
- `THESIS_LLM_PROVIDER`: Currently defaults to `rule_based`.
- `THESIS_LLM_PROVIDER=openai_compatible`: Enables the OpenAI-compatible JSON LLM provider.
- `THESIS_LLM_ENDPOINT` / `THESIS_LLM_API_KEY` / `THESIS_LLM_MODEL`: Configuration for LLM-backed structure recognition.

## 样例文件 / Sample Files

- `samples/input/demo_thesis.docx`: 最小 demo 论文输入文件。
- `samples/realistic_swufe/swufe_before_anonymized.docx`: 来自真实修改前论文的脱敏格式镜像。
- `samples/realistic_swufe/swufe_after_anonymized.docx`: 来自真实修改后论文的脱敏格式镜像。
- `samples/realistic_swufe/format_delta.json`: 前后格式差异摘要，不包含真实正文。
- `samples/realistic_swufe/policy_rules_used.json`: 从西南财经大学政策文件整理出的 demo 规则要点。
- `samples/output/example_format_report.json`: 代表性的校验报告 payload。
- `scripts/create_sample_docx.py`: 重新生成 demo 输入文件。
- `scripts/build_anonymized_real_demo.py`: 从本机真实前后 DOCX 生成脱敏 SWUFE demo 资产。

- `samples/input/demo_thesis.docx`: Minimal demo thesis input.
- `samples/realistic_swufe/swufe_before_anonymized.docx`: Format-preserving anonymized mirror of a real before document.
- `samples/realistic_swufe/swufe_after_anonymized.docx`: Format-preserving anonymized mirror of a real after document.
- `samples/realistic_swufe/format_delta.json`: Before/after format delta summary with no real thesis body text.
- `samples/realistic_swufe/policy_rules_used.json`: Demo rule highlights derived from the SWUFE policy document.
- `samples/output/example_format_report.json`: Representative validation report payload.
- `scripts/create_sample_docx.py`: Regenerates the demo input.
- `scripts/build_anonymized_real_demo.py`: Builds anonymized SWUFE demo assets from local real before/after DOCX files.

## 当前能力边界 / Current Capability Boundaries

MVP 当前可以使用 `python-docx` 解析段落、section、页边距、页眉和页脚；构建块级 IR；用启发式规则识别常见论文章节；应用基础页边距、段落样式、页眉页脚修复；并输出校验报告。

新增 Open XML 引擎后，系统可以直接改写 Word XML 中的 section 属性、页脚 PAGE 域、页码重启和目录 dirty 标记。LLM-backed 结构识别仍然只输出结构标签和解释，规则引擎仍是格式修复的唯一执行来源。

The MVP can parse paragraphs, sections, margins, headers, and footers with `python-docx`; build a block-level IR; identify common thesis sections using deterministic heuristics; apply basic margins, paragraph styles, headers, and footers; and produce validation reports.

With the Open XML engine, the system can directly rewrite Word XML section properties, footer PAGE fields, page-number restarts, and TOC dirty markers. LLM-backed structure recognition only outputs labels and explanations; the rule engine remains the sole authority for repair execution.

已知限制：

- 脱敏样例保留格式结构和字段形态，但不保留真实论文正文或图片内容。
- Open XML 引擎当前标记目录为 dirty，让 Word 打开文档后刷新；它不会在服务器端重新计算完整目录页码。
- 当前结构识别器是启发式规则，不是训练好的分类模型。
- 真实学校规则需要基于官方格式指南编码，并配套 fixture 文档测试。
- LLM provider 的生产集成应加入更完整的 prompt/version 日志、失败重试、成本控制和安全 fallback。

Known limitations:

- Anonymized samples preserve formatting structure and field shape, but not real thesis body text or image content.
- The Open XML engine currently marks the TOC as dirty so Word can refresh it when opened; it does not recalculate full TOC page numbers server-side.
- The current recognizer is heuristic, not a trained classifier.
- Real school rules should be encoded from official formatting guides and covered with fixture documents.
- Production LLM integration should add richer prompt/version logging, retries, cost controls, and safe fallback behavior.

## 后续方向 / Roadmap

- 扩展 Open XML 引擎的目录和页码验证能力，例如打开 Word 前后的字段状态检测。
- 为每条学校规则增加 golden DOCX fixture 测试。
- 为 LLM-backed 结构识别增加离线评测集、提示词版本管理和置信度阈值策略。
- 为大文档处理增加进度轮询和持久化 job 记录。
- 增加更丰富的 before/after 格式证据报告。

- Extend Open XML TOC and page-number validation, including field-state checks before and after opening in Word.
- Add fixture-based golden DOCX tests for each school rule.
- Add offline evaluation sets, prompt versioning, and confidence thresholding for LLM-backed structure recognition.
- Add progress polling and persisted job records for larger documents.
- Add richer report diffs showing before/after formatting evidence.
