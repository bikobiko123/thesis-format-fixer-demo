# Thesis Format Fixer Agent-First Design

## Goal

Build a local agent tool for pre-submission university thesis formatting repair. An agent or shell user passes a `.docx` thesis to the CLI and receives a repaired `.docx`, validation report, and remaining manual-fix checklist.

## Scope

The demo supports one school-oriented profile, undergraduate and master rule sets, and `.docx` documents only. It does not implement a Word plugin, Web upload UI, PDF pipeline, or thesis content generation.

## Architecture

The backend is a local Python package organized into rule loading, DOCX parsing/repair, thesis IR, structure recognition, deterministic repair planning, validation, reporting, and LLM provider abstraction. The DOCX engine supports a `python-docx` implementation and an Open XML implementation behind the same protocol.

The product surface is now CLI and agent packaging:

1. `python3.12 -m app.cli repair` runs the formatter.
2. `skills/thesis-format-fixer` documents safe agent usage.
3. `plugins/thesis-format-fixer` packages the skill as a repo-local Codex plugin.
4. `.claude/commands/thesis-fix.md` gives Claude Code a command template.

## Data Flow

1. Agent confirms the input is `.docx`.
2. CLI chooses rule profile, DOCX engine, and structure recognizer.
3. DOCX engine extracts paragraph, style, section, header, and footer metadata.
4. Structure recognizer converts parsed data into block-level IR.
5. Rule-based repair planner maps IR blocks and rule JSON into deterministic operations.
6. DOCX engine applies formatting operations and saves `repaired_thesis.docx`.
7. Validator emits `pass` / `warn` / `fail` items.
8. Report generator writes JSON, Markdown, manual checklist, and zip archive.
9. Agent reports output paths and remaining manual fixes.

## Boundaries

The LLM provider is not allowed to directly mutate the document. It can propose structure labels and explanations only. Rules remain the source of truth for repair decisions.

## Testing

The backend includes tests for rule loading, recognizer behavior, validation output, Open XML operations, CLI output artifacts, agent packaging, and an end-to-end DOCX processing path that verifies zip contents.
