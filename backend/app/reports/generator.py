import json
from dataclasses import asdict
from pathlib import Path

from app.ir.models import ThesisDocument
from app.repair.engine import RepairPlan
from app.validation.validator import ValidationReport


class ReportGenerator:
    def write_reports(
        self,
        output_dir: Path,
        ir: ThesisDocument,
        validation: ValidationReport,
        repair_plan: RepairPlan,
        structure_explanations: dict[int, str],
    ) -> dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_payload = {
            "metadata": ir.metadata,
            "degree": ir.degree,
            "summary": validation.summary,
            "repair_summary": repair_plan.summary,
            "items": [asdict(item) for item in validation.items],
            "structure_explanations": structure_explanations,
        }

        json_path = output_dir / "format_report.json"
        json_path.write_text(
            json.dumps(report_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        markdown_path = output_dir / "format_report.md"
        markdown_path.write_text(self._markdown(report_payload), encoding="utf-8")

        manual_path = output_dir / "manual_fix_list.md"
        manual_items = validation.manual_fix_list or ["No remaining manual fixes were detected."]
        manual_path.write_text(
            "# Remaining Manual Fix List\n\n"
            + "\n".join(f"- {item}" for item in manual_items)
            + "\n",
            encoding="utf-8",
        )
        return {"json": json_path, "markdown": markdown_path, "manual": manual_path}

    def _markdown(self, payload: dict) -> str:
        lines = [
            "# Thesis Format Validation Report",
            "",
            f"- Degree: {payload['degree']}",
            f"- Rule version: {payload['metadata'].get('rule_version', 'unknown')}",
            f"- Summary: {payload['summary']}",
            f"- Repair operations: {payload['repair_summary']}",
            "",
            "## Validation Items",
        ]
        for item in payload["items"]:
            lines.append(f"- **{item['status'].upper()}** `{item['rule_id']}`: {item['message']}")
            if item.get("manual_action"):
                lines.append(f"  Manual action: {item['manual_action']}")
        lines.extend(["", "## Structure Explanations"])
        for index, explanation in payload["structure_explanations"].items():
            lines.append(f"- Paragraph {index}: {explanation}")
        return "\n".join(lines) + "\n"
