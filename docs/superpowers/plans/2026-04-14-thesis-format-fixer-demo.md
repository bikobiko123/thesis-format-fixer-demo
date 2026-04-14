# Thesis Format Fixer Agent-First Implementation Plan

> Supersedes the initial Web demo plan. The project now ships as a CLI, Codex skill, repo-local Codex plugin, and Claude Code command template.

**Goal:** Build a runnable agent tool for `.docx` thesis format repair.

**Architecture:** Keep DOCX IO, IR, recognition, repair, validation, reporting, CLI, and agent packaging as separate modules. Use `python-docx` and Open XML behind a shared abstraction.

**Tech Stack:** Python 3.12, python-docx, pytest, Open XML, Codex skills/plugins.

---

### Task 1: Backend Rule, IR, And Validation Core

- [x] Implement rule schemas and JSON rule profiles.
- [x] Implement block-level IR data classes.
- [x] Implement heuristic structure recognizer.
- [x] Implement validator with `pass` / `warn` / `fail`.

### Task 2: DOCX Engine And Processing Service

- [x] Define `DocxEngine` protocol.
- [x] Implement `PythonDocxEngine.parse`.
- [x] Implement Open XML operations for margins, page fields, section breaks, page-number restarts, and TOC dirty flags.
- [x] Generate report JSON, report Markdown, manual checklist, and result zip.

### Task 3: Agent CLI

- [x] Add `backend/app/cli.py`.
- [x] Expose the `thesis-fix` console script.
- [x] Write predictable artifacts for agents: repaired DOCX, JSON report, Markdown report, manual checklist, and zip archive.
- [x] Add CLI smoke tests.

### Task 4: Agent Packaging

- [x] Add `skills/thesis-format-fixer`.
- [x] Add `plugins/thesis-format-fixer`.
- [x] Add `.agents/plugins/marketplace.json`.
- [x] Add `.claude/commands/thesis-fix.md`.
- [x] Add packaging integrity tests.

### Task 5: Documentation And Samples

- [x] Document current scope, CLI usage, tests, module boundaries, limitations, and roadmap.
- [x] Generate sample `.docx` input.
- [x] Add anonymized SWUFE before/after sample assets.
- [x] Keep README bilingual in Chinese and English.
