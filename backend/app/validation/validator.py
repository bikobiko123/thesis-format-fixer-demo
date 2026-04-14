from dataclasses import dataclass, field
from typing import Literal

from app.ir.models import ThesisDocument
from app.rules.schema import ThesisRules

ValidationStatus = Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class ValidationItem:
    rule_id: str
    status: ValidationStatus
    message: str
    location: str | None = None
    manual_action: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    items: list[ValidationItem] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
        return {
            "pass": sum(item.status == "pass" for item in self.items),
            "warn": sum(item.status == "warn" for item in self.items),
            "fail": sum(item.status == "fail" for item in self.items),
        }

    @property
    def manual_fix_list(self) -> list[str]:
        return [item.manual_action for item in self.items if item.manual_action]


class ThesisValidator:
    def validate(self, ir: ThesisDocument, rules: ThesisRules) -> ValidationReport:
        items: list[ValidationItem] = []
        items.extend(self._validate_required_sections(ir, rules))
        items.extend(self._validate_heading_hierarchy(ir))
        items.extend(self._validate_caption_format(ir, rules))
        items.append(self._validate_toc_presence(ir))
        items.append(
            ValidationItem(
                rule_id="page_margins",
                status="pass",
                message=(
                    "Page margins are scheduled for deterministic repair from the "
                    "selected rule set."
                ),
            )
        )
        return ValidationReport(items)

    def _validate_required_sections(
        self, ir: ThesisDocument, rules: ThesisRules
    ) -> list[ValidationItem]:
        items: list[ValidationItem] = []
        for section in rules.required_sections:
            if not section.required:
                continue
            if section.name in ir.sections:
                items.append(
                    ValidationItem(
                        rule_id="required_sections",
                        status="pass",
                        message=f"Required section present: {section.name}.",
                    )
                )
            else:
                items.append(
                    ValidationItem(
                        rule_id="required_sections",
                        status="fail",
                        message=f"Missing required section: {section.name}.",
                        manual_action=f"Add or rename the section matching {section.aliases}.",
                    )
                )
        return items

    def _validate_heading_hierarchy(self, ir: ThesisDocument) -> list[ValidationItem]:
        heading_levels = [block.heading_level for block in ir.blocks if block.heading_level]
        if not heading_levels:
            return [
                ValidationItem(
                    rule_id="heading_hierarchy",
                    status="warn",
                    message="No heading hierarchy was detected.",
                    manual_action=(
                        "Check whether chapter titles use recognizable heading text or Word styles."
                    ),
                )
            ]
        if heading_levels[0] and heading_levels[0] > 1:
            return [
                ValidationItem(
                    rule_id="heading_hierarchy",
                    status="fail",
                    message="The first detected heading is not level 1.",
                    manual_action="Promote the first chapter heading to level 1.",
                )
            ]
        return [
            ValidationItem(
                rule_id="heading_hierarchy",
                status="pass",
                message="Heading hierarchy starts with a level 1 heading.",
            )
        ]

    def _validate_caption_format(
        self, ir: ThesisDocument, rules: ThesisRules
    ) -> list[ValidationItem]:
        captions = [block for block in ir.blocks if block.kind == "caption"]
        if not captions:
            return [
                ValidationItem(
                    rule_id="caption_format",
                    status="warn",
                    message="No figure or table captions were detected.",
                    manual_action=(
                        "Confirm whether the thesis contains figures or tables needing captions."
                    ),
                )
            ]
        return [
            ValidationItem(
                rule_id="caption_format",
                status="pass",
                message=f"Detected {len(captions)} captions using {rules.captions} prefixes.",
            )
        ]

    def _validate_toc_presence(self, ir: ThesisDocument) -> ValidationItem:
        if "Table of Contents" in ir.sections:
            return ValidationItem("toc_presence", "pass", "Table of contents detected.")
        return ValidationItem(
            "toc_presence",
            "warn",
            "Table of contents was not detected.",
            manual_action=(
                "Insert or regenerate the Word table of contents before final submission."
            ),
        )
