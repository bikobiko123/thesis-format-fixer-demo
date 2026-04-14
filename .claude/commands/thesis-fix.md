# thesis-fix

Repair a DOCX thesis format without changing thesis content.

Use from the repository root:

```bash
python3.12 -m pip install -e '.[dev]'
python3.12 -m app.cli repair \
  --input "$ARGUMENTS" \
  --profile swufe_master \
  --out ./outputs/thesis-fix \
  --docx-engine openxml \
  --structure-recognizer heuristic
```

After running, report these files:

- `outputs/thesis-fix/repaired_thesis.docx`
- `outputs/thesis-fix/format_report.md`
- `outputs/thesis-fix/manual_fix_list.md`
- `outputs/thesis-fix/thesis_format_fix_result.zip`

Do not rewrite or summarize thesis content. Only explain formatting results and remaining manual fixes.
