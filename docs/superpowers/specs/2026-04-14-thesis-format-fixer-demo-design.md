# Thesis Format Fixer Demo Design

## Goal

Build a runnable demo Web tool for pre-submission university thesis formatting repair. Users upload a `.docx` thesis and receive a zip containing the repaired `.docx`, validation report, and remaining manual-fix checklist.

## Scope

The demo supports one school, undergraduate and master rule sets, and `.docx` documents only. It does not implement a Word plugin, PDF pipeline, or thesis content generation.

## Architecture

The backend is a FastAPI app organized into rule loading, DOCX parsing/repair, thesis IR, structure recognition, deterministic repair planning, validation, reporting, and LLM provider abstraction. The current DOCX engine uses `python-docx` behind a protocol so a lower-level Open XML engine can replace it later without rewriting the service layer.

The frontend is a React/Vite upload workbench. It submits multipart uploads to `/api/process` and downloads the returned result zip.

## Data Flow

1. User selects degree and uploads `.docx`.
2. FastAPI validates extension and size, then stores a temporary upload.
3. `PythonDocxEngine` extracts paragraph, style, section, header, and footer metadata.
4. `HeuristicStructureRecognizer` converts parsed data into block-level IR.
5. `RuleBasedRepairPlanner` maps IR blocks and rule JSON into deterministic operations.
6. DOCX engine applies formatting operations and saves `repaired_thesis.docx`.
7. Validator emits `pass` / `warn` / `fail` items.
8. Report generator writes JSON, Markdown, and manual checklist.
9. Service returns a zip archive.

## Boundaries

The LLM provider is not allowed to directly mutate the document. It can explain detected structure and validation errors. Rules remain the source of truth for repair decisions.

## Testing

The backend includes tests for rule loading, recognizer behavior, validation output, API health, and an end-to-end DOCX processing path that verifies zip contents.
