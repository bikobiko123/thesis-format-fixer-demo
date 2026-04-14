from app.docx_engine.base import DocxDocumentInfo, ParagraphInfo
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
