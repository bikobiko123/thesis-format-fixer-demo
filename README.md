# Thesis Format Fixer Demo

高校毕业论文格式智能修复系统 demo。用户上传 `.docx` 论文后，系统返回：

- 修复后的 `.docx`
- 格式校验报告 `format_report.json` / `format_report.md`
- 剩余人工修复清单 `manual_fix_list.md`

This MVP favors a runnable, modular slice over complete university-specific formatting coverage.

## Product Scope

In scope:

- One demo school: `Demo University`
- Two degree tracks: undergraduate and master
- Only `.docx`
- Thesis pre-submission formatting repair
- Rule-based deterministic repair with LLM provider abstraction for structure/error explanations

Out of scope:

- Word plugins
- PDF processing
- Thesis content generation
- Multi-school rule marketplace
- Legal guarantee that the repaired document satisfies a real university's final office review

## Architecture

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

Key backend modules:

- `backend/app/rules`: JSON schema and rule loading for undergraduate/master tracks.
- `backend/app/docx_engine`: `DocxEngine` protocol plus current `python-docx` implementation, reserved for future Open XML replacement.
- `backend/app/ir`: thesis structure and block-level intermediate representation.
- `backend/app/structure`: heuristic recognizer for abstracts, heading levels, body, references, appendix, captions, and acknowledgements.
- `backend/app/repair`: deterministic formatting repair plan generation.
- `backend/app/validation`: `pass` / `warn` / `fail` validation report.
- `backend/app/llm`: provider abstraction. The MVP ships an offline rule-based provider so the demo runs without API keys.
- `backend/app/reports`: user-readable JSON/Markdown/manual-fix outputs.

## Quick Start

Install backend dependencies:

```bash
python3.12 -m pip install -e '.[dev]'
```

Run backend:

```bash
uvicorn app.main:app --app-dir backend --reload
```

Run frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`, upload `samples/input/demo_thesis.docx`, and download the generated zip result.

## Tests

```bash
python3.12 -m pytest backend/tests -q
```

Current coverage includes rule loading, structure recognition, validator output, API health, and end-to-end DOCX processing into a result zip.

## Configuration

Copy `.env.example` to `.env`.

Important variables:

- `THESIS_ALLOWED_ORIGINS`: CORS origins for the frontend.
- `THESIS_STORAGE_DIR`: output workspace for repaired files and reports.
- `THESIS_LLM_PROVIDER`: currently defaults to `rule_based`.
- `THESIS_LLM_API_KEY`: reserved for future cloud/local LLM integrations.

## Sample Files

- `samples/input/demo_thesis.docx`: minimal demo thesis input.
- `samples/output/example_format_report.json`: representative validation report payload.
- `scripts/create_sample_docx.py`: regenerates the demo input.

## Current Capability Boundaries

The MVP can parse paragraphs, sections, margins, headers, and footers with `python-docx`; build a block-level IR; identify common thesis sections using deterministic heuristics; apply basic margins, paragraph styles, headers, and footers; and produce validation reports.

Known limitations:

- `python-docx` cannot fully update Word fields such as a real dynamic table of contents.
- Section-break and page-number behavior is basic and should be upgraded with raw Open XML for production.
- The current recognizer is heuristic, not a trained classifier.
- Real school rules should be encoded from official formatting guides and covered with fixture documents.
- The LLM provider is a deterministic placeholder; production integrations should add prompt/version logging and safe fallback behavior.

## Roadmap

- Add raw Open XML engine for field codes, section breaks, page-number restarts, and TOC updates.
- Add fixture-based golden DOCX tests for each school rule.
- Add an LLM-backed structure recognizer that only proposes labels and explanations, while rules remain the repair authority.
- Add progress polling and persisted job records for larger documents.
- Add richer report diffs showing before/after formatting evidence.
