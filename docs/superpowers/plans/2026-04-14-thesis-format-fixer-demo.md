# Thesis Format Fixer Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable FastAPI + React demo for `.docx` thesis format repair.

**Architecture:** Keep DOCX IO, IR, recognition, repair, validation, reporting, and Web API as separate modules. Use `python-docx` behind an abstraction so Open XML can replace it later.

**Tech Stack:** Python 3.12, FastAPI, python-docx, pytest, React, Vite.

---

### Task 1: Backend Rule, IR, And Validation Core

**Files:**

- Create: `backend/app/rules/schema.py`
- Create: `backend/app/rules/loader.py`
- Create: `backend/app/rules/data/undergraduate.json`
- Create: `backend/app/rules/data/master.json`
- Create: `backend/app/ir/models.py`
- Create: `backend/app/structure/recognizer.py`
- Create: `backend/app/validation/validator.py`
- Test: `backend/tests/test_rules.py`
- Test: `backend/tests/test_structure_recognizer.py`
- Test: `backend/tests/test_validator.py`

- [x] Write failing tests for rule loading, block classification, and missing required sections.
- [x] Implement pydantic rule schema and JSON loaders.
- [x] Implement block-level IR data classes.
- [x] Implement heuristic structure recognizer.
- [x] Implement validator with `pass` / `warn` / `fail`.
- [x] Run `python3.12 -m pytest backend/tests -q`.

### Task 2: DOCX Engine And Processing Service

**Files:**

- Create: `backend/app/docx_engine/base.py`
- Create: `backend/app/docx_engine/python_docx.py`
- Create: `backend/app/repair/engine.py`
- Create: `backend/app/reports/generator.py`
- Create: `backend/app/services/processor.py`
- Create: `backend/tests/test_processor.py`

- [x] Define `DocxEngine` protocol for future Open XML replacement.
- [x] Implement `PythonDocxEngine.parse`.
- [x] Implement repair operations for margins, paragraph styles, headers, and footers.
- [x] Generate report JSON, report Markdown, manual checklist, and result zip.
- [x] Run end-to-end processor test.

### Task 3: FastAPI Web API

**Files:**

- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/exceptions.py`
- Create: `backend/app/core/logging.py`
- Create: `backend/tests/test_api.py`

- [x] Add `.env`-based settings.
- [x] Add CORS and health endpoint.
- [x] Add `/api/process` multipart upload endpoint.
- [x] Convert domain exceptions to HTTP errors.
- [x] Run API health test.

### Task 4: React Frontend

**Files:**

- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/.env.example`

- [x] Add Vite React app shell.
- [x] Implement degree selection, `.docx` upload, process call, and zip download.
- [x] Add a distinctive academic-paper workbench visual style.
- [x] Run `npm install` and `npm run build`.

### Task 5: Documentation, Samples, And GitHub Publish

**Files:**

- Create: `README.md`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `scripts/create_sample_docx.py`
- Create: `samples/input/demo_thesis.docx`
- Create: `samples/output/example_format_report.json`

- [x] Document current scope, quick start, tests, module boundaries, limitations, and roadmap.
- [x] Generate sample `.docx` input.
- [x] Initialize git repository.
- [x] Commit and push to GitHub.
