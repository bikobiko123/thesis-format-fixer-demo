from app.ir.models import ThesisBlock, ThesisDocument
from app.repair.engine import RuleBasedRepairPlanner
from app.rules.loader import load_rules


def test_repair_planner_uses_level_one_style_for_abstract_titles() -> None:
    ir = ThesisDocument(
        degree="master",
        blocks=[
            ThesisBlock(index=0, text="摘要", kind="abstract", heading_level=1),
            ThesisBlock(index=1, text="Abstract", kind="abstract", heading_level=1),
        ],
        sections={},
    )

    plan = RuleBasedRepairPlanner().plan(ir, load_rules("swufe_master"))
    style_ops = [
        operation
        for operation in plan.operations
        if operation.get("type") == "set_paragraph_style"
    ]

    assert [operation["style_key"] for operation in style_ops] == ["heading_1", "heading_1"]


def test_repair_planner_preserves_bibliography_style_entries() -> None:
    ir = ThesisDocument(
        degree="master",
        blocks=[
            ThesisBlock(
                index=0,
                text="[1] Citation entry",
                kind="body",
                source_style="Bibliography",
            )
        ],
        sections={},
    )

    plan = RuleBasedRepairPlanner().plan(ir, load_rules("swufe_master"))

    assert not any(
        operation.get("type") == "set_paragraph_style"
        and operation.get("paragraph_index") == 0
        for operation in plan.operations
    )
