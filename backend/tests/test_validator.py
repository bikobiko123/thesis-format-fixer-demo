from app.docx_engine.base import DocxDocumentInfo, ParagraphInfo
from app.ir.models import ThesisDocument, ThesisSection
from app.rules.loader import load_rules
from app.structure.recognizer import HeuristicStructureRecognizer
from app.validation.validator import ThesisValidator


def test_validator_reports_missing_required_sections() -> None:
    doc = DocxDocumentInfo(
        paragraphs=[ParagraphInfo(index=0, text="第一章 绪论", style_name="Heading 1")],
        sections=[],
        headers=[],
        footers=[],
    )
    rules = load_rules("undergraduate")
    ir = HeuristicStructureRecognizer().recognize(doc, rules)

    report = ThesisValidator().validate(ir, rules)

    assert report.summary["fail"] >= 1
    assert any(item.rule_id == "required_sections" for item in report.items)


def test_validator_warns_when_toc_can_be_regenerated_by_word() -> None:
    ir = ThesisDocument(
        degree="master",
        blocks=[],
        sections={
            "Chinese Abstract": ThesisSection("Chinese Abstract", 0),
            "English Abstract": ThesisSection("English Abstract", 1),
            "Introduction": ThesisSection("Introduction", 2),
            "Body": ThesisSection("Body", 2),
            "References": ThesisSection("References", 3),
        },
    )

    report = ThesisValidator().validate(ir, load_rules("swufe_master"))
    toc_items = [
        item
        for item in report.items
        if item.rule_id == "required_sections" and "Table of Contents" in item.message
    ]

    assert toc_items[0].status == "warn"


def test_validator_warns_when_toc_field_needs_update() -> None:
    ir = ThesisDocument(
        degree="master",
        blocks=[],
        sections={"Table of Contents": ThesisSection("Table of Contents", 0)},
        metadata={"toc_needs_update": "true"},
    )

    report = ThesisValidator().validate(ir, load_rules("undergraduate"))

    toc_items = [item for item in report.items if item.rule_id == "toc_presence"]
    assert toc_items[0].status == "warn"
