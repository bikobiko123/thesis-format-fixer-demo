---
name: thesis-format-fixer
description: Use when Codex needs to repair or validate a DOCX university thesis format, especially Chinese graduate thesis submissions, SWUFE thesis rules, before/after thesis format demos, or requests that need repaired .docx, validation report, and manual-fix checklist without changing thesis content.
---

# Thesis Format Fixer

## Core Rule

Never generate, rewrite, summarize, or “improve” thesis content. Only inspect structure and formatting, run deterministic repair, and explain remaining manual work.

LLM structure recognition may propose labels and explanations only. The rule engine is the only authority allowed to decide and execute formatting repairs.

## Quick Start

From this repository root:

```bash
python3.12 -m pip install -e '.[dev]'
python3.12 -m app.cli repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out /absolute/path/to/output-dir \
  --docx-engine openxml \
  --structure-recognizer heuristic
```

The output directory contains:

- `repaired_thesis.docx`
- `format_report.json`
- `format_report.md`
- `manual_fix_list.md`
- `thesis_format_fix_result.zip`

## Workflow

1. Confirm the input is `.docx`. Do not accept PDF or `.doc` for repair.
2. Choose a profile. Use `swufe_master` for 西南财经大学硕士论文.
3. Run the CLI. Prefer `--docx-engine openxml`.
4. Use `--structure-recognizer heuristic` by default. Use `llm` only when the user asks for LLM-backed structure recognition or when headings are too ambiguous.
5. Read `format_report.md` and `manual_fix_list.md`.
6. Tell the user where the repaired file and checklist are.

## LLM Mode

Use LLM mode only as a structure-label helper:

```bash
python3.12 -m app.cli repair \
  --input /absolute/path/to/thesis.docx \
  --profile swufe_master \
  --out /absolute/path/to/output-dir \
  --docx-engine openxml \
  --structure-recognizer llm \
  --llm-provider openai_compatible \
  --llm-endpoint "$THESIS_LLM_ENDPOINT" \
  --llm-api-key "$THESIS_LLM_API_KEY" \
  --llm-model "${THESIS_LLM_MODEL:-gpt-4o-mini}"
```

If LLM labeling fails, fall back to heuristic mode. Do not block deterministic repair on LLM availability.

## References

- `references/format-boundaries.md`: safety and scope boundaries.
- `references/swufe-master-policy.md`: SWUFE master thesis formatting rules encoded by this demo.
- `assets/rules/swufe_master.json`: rule JSON snapshot.
