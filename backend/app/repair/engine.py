from dataclasses import dataclass, field

from app.ir.models import ThesisDocument
from app.rules.schema import StyleRule, ThesisRules


@dataclass(frozen=True)
class RepairPlan:
    operations: list[dict] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for operation in self.operations:
            op_type = operation["type"]
            counts[op_type] = counts.get(op_type, 0) + 1
        return counts


def _style_payload(style: StyleRule) -> dict:
    return style.model_dump()


class RuleBasedRepairPlanner:
    """Builds deterministic formatting operations from rules and recognized blocks."""

    def plan(self, ir: ThesisDocument, rules: ThesisRules) -> RepairPlan:
        operations: list[dict] = [
            {"type": "set_margins", "margins": rules.page_setup.model_dump()},
            {
                "type": "ensure_page_number_footer",
                "restart_at_body": rules.page_numbers.start_at_body,
            },
            {"type": "mark_toc_dirty"},
            {
                "type": "ensure_header_text",
                "text": f"{rules.school} {rules.degree} thesis",
            },
        ]

        for block in ir.blocks:
            if (block.source_style or "").lower() == "bibliography":
                continue
            style_key = self._style_key(block.kind)
            if block.kind == "heading_1" and block.index > 0:
                operations.append(
                    {"type": "ensure_section_break_before", "paragraph_index": block.index}
                )
            if style_key in rules.styles:
                operations.append(
                    {
                        "type": "set_paragraph_style",
                        "paragraph_index": block.index,
                        "style_key": style_key,
                        "style": _style_payload(rules.styles[style_key]),
                    }
                )

        return RepairPlan(operations)

    def _style_key(self, block_kind: str) -> str:
        if block_kind == "title":
            return "title"
        if block_kind in {
            "heading_1",
            "abstract",
            "toc",
            "references",
            "appendix",
            "acknowledgements",
        }:
            return "heading_1"
        if block_kind == "heading_3":
            return "heading_3"
        if block_kind == "heading_2":
            return "heading_2"
        if block_kind == "caption":
            return "caption"
        return "body"
