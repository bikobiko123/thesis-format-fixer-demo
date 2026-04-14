from app.docx_engine.base import DocxDocumentInfo, ParagraphInfo
from app.ir.models import ThesisBlock
from app.llm.base import StructureLabel
from app.llm.provider import RuleBasedLLMProvider
from app.rules.loader import load_rules
from app.structure.llm_recognizer import LLMStructureRecognizer
from app.structure.recognizer import HeuristicStructureRecognizer


class FakeProvider(RuleBasedLLMProvider):
    def propose_structure_labels(self, blocks: list[ThesisBlock]) -> dict[int, StructureLabel]:
        return {
            0: StructureLabel(kind="abstract", explanation="LLM recognized an abstract heading."),
            1: StructureLabel(
                kind="references", explanation="LLM recognized a references heading."
            ),
        }


def test_llm_recognizer_overlays_labels_but_does_not_emit_repairs() -> None:
    doc = DocxDocumentInfo(
        paragraphs=[
            ParagraphInfo(index=0, text="内容摘要", style_name="Normal"),
            ParagraphInfo(index=1, text="主要文献", style_name="Normal"),
        ],
        sections=[],
        headers=[],
        footers=[],
    )

    recognizer = LLMStructureRecognizer(HeuristicStructureRecognizer(), FakeProvider())
    ir = recognizer.recognize(doc, load_rules("swufe_master"))

    assert [block.kind for block in ir.blocks] == ["abstract", "references"]
    assert "LLM recognized an abstract heading." in ir.blocks[0].notes
    assert "Chinese Abstract" in ir.sections
    assert "References" in ir.sections
