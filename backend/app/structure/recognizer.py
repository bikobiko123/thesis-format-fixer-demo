import re

from app.docx_engine.base import DocxDocumentInfo, ParagraphInfo
from app.ir.models import BlockKind, ThesisBlock, ThesisDocument, ThesisSection
from app.rules.schema import ThesisRules

CAPTION_PATTERN = re.compile(r"^(图|表)\s?\d+([-\.]\d+)*\s+.+")
NUMBERED_HEADING_PATTERN = re.compile(r"^\d+(\.\d+){0,2}\s+.+")
CHAPTER_PATTERN = re.compile(r"^第[一二三四五六七八九十0-9]+[章节]\s*.+")


class HeuristicStructureRecognizer:
    """Local deterministic recognizer used before optional LLM enrichment."""

    def recognize(self, doc: DocxDocumentInfo, rules: ThesisRules) -> ThesisDocument:
        blocks = [self._classify(paragraph) for paragraph in doc.paragraphs if paragraph.text]
        sections = self._build_sections(blocks, rules)
        return ThesisDocument(
            degree=rules.degree,
            blocks=blocks,
            sections=sections,
            metadata={"school": rules.school, "rule_version": rules.version},
        )

    def _classify(self, paragraph: ParagraphInfo) -> ThesisBlock:
        text = paragraph.text.strip()
        style = paragraph.style_name or ""
        lower_style = style.lower()

        kind: BlockKind = "body"
        level: int | None = None
        confidence = 0.72
        notes: list[str] = []

        if text in {"摘要", "中文摘要"}:
            kind, level, confidence = "abstract", 1, 0.98
        elif text in {"Abstract", "ABSTRACT"}:
            kind, level, confidence = "abstract", 1, 0.96
        elif text.startswith(("关键词", "Key words", "Keywords")):
            kind, confidence = "keywords", 0.95
        elif text == "目录":
            kind, level, confidence = "toc", 1, 0.98
        elif text == "参考文献":
            kind, level, confidence = "references", 1, 0.99
        elif text.startswith("附录"):
            kind, level, confidence = "appendix", 1, 0.94
        elif text == "致谢":
            kind, level, confidence = "acknowledgements", 1, 0.94
        elif CAPTION_PATTERN.match(text):
            kind, confidence = "caption", 0.96
        elif "heading 1" in lower_style or CHAPTER_PATTERN.match(text):
            kind, level, confidence = "heading_1", 1, 0.9
        elif "heading 2" in lower_style or NUMBERED_HEADING_PATTERN.match(text):
            kind, level, confidence = "heading_2", 2, 0.86
        elif paragraph.index == 0 and len(text) <= 60:
            kind, confidence = "title", 0.75
            notes.append("First non-empty paragraph treated as candidate title.")

        return ThesisBlock(
            index=paragraph.index,
            text=text,
            kind=kind,
            source_style=paragraph.style_name,
            heading_level=level,
            confidence=confidence,
            notes=notes,
        )

    def _build_sections(
        self, blocks: list[ThesisBlock], rules: ThesisRules
    ) -> dict[str, ThesisSection]:
        sections: dict[str, ThesisSection] = {}
        normalized_aliases = {
            alias.lower(): section
            for section in rules.required_sections
            for alias in section.aliases
        }
        kind_to_section = {
            "abstract": "Chinese Abstract",
            "toc": "Table of Contents",
            "references": "References",
            "appendix": "Appendix",
            "acknowledgements": "Acknowledgements",
        }

        for offset, block in enumerate(blocks):
            matched = kind_to_section.get(block.kind)
            if block.text.lower() in normalized_aliases:
                matched = normalized_aliases[block.text.lower()].name
            if block.kind == "heading_1" and "Body" not in sections:
                matched = "Body"
            if matched and matched not in sections:
                rule = next(
                    (rule for rule in rules.required_sections if rule.name == matched), None
                )
                sections[matched] = ThesisSection(
                    name=matched,
                    start_block=block.index,
                    end_block=blocks[offset + 1].index - 1 if offset + 1 < len(blocks) else None,
                    required=rule.required if rule else False,
                )
        return sections
