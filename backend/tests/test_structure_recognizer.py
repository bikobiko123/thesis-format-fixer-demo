from app.docx_engine.base import DocxDocumentInfo, ParagraphInfo
from app.rules.loader import load_rules
from app.structure.recognizer import HeuristicStructureRecognizer


def test_recognizer_classifies_required_blocks_and_captions() -> None:
    doc = DocxDocumentInfo(
        paragraphs=[
            ParagraphInfo(index=0, text="摘要", style_name="Heading 1"),
            ParagraphInfo(index=1, text="关键词：智能修复；论文格式", style_name="Normal"),
            ParagraphInfo(index=2, text="第一章 绪论", style_name="Heading 1"),
            ParagraphInfo(index=3, text="图1-1 系统架构", style_name="Normal"),
            ParagraphInfo(index=4, text="参考文献", style_name="Heading 1"),
        ],
        sections=[],
        headers=[],
        footers=[],
    )

    ir = HeuristicStructureRecognizer().recognize(doc, load_rules("undergraduate"))

    kinds = [block.kind for block in ir.blocks]
    assert "abstract" in kinds
    assert "heading_1" in kinds
    assert "caption" in kinds
    assert ir.sections["Chinese Abstract"].start_block == 0
    assert ir.sections["References"].start_block == 4


def test_recognizer_matches_section_aliases_inside_realistic_short_headings() -> None:
    doc = DocxDocumentInfo(
        paragraphs=[
            ParagraphInfo(index=0, text="摘要", style_name="Heading 1"),
            ParagraphInfo(index=1, text="ABSTRACT", style_name="Heading 1"),
            ParagraphInfo(index=2, text="绪论", style_name="西财硕论一级"),
        ],
        sections=[],
        headers=[],
        footers=[],
    )

    ir = HeuristicStructureRecognizer().recognize(doc, load_rules("swufe_master"))

    assert ir.blocks[2].kind == "heading_1"
    assert ir.sections["Introduction"].start_block == 2
