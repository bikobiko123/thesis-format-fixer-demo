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
        if doc.has_toc_field and "Table of Contents" not in sections:
            sections["Table of Contents"] = ThesisSection(
                name="Table of Contents",
                start_block=blocks[0].index if blocks else 0,
                required=True,
            )
        return ThesisDocument(
            degree=rules.degree,
            blocks=blocks,
            sections=sections,
            metadata={
                "school": rules.school,
                "rule_version": rules.version,
                "toc_needs_update": str(doc.toc_needs_update).lower(),
            },
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
        elif _style_is_heading(lower_style, 1) or CHAPTER_PATTERN.match(text):
            kind, level, confidence = "heading_1", 1, 0.9
        elif _style_is_heading(lower_style, 2):
            kind, level, confidence = "heading_2", 2, 0.86
        elif _style_is_heading(lower_style, 3):
            kind, level, confidence = "heading_3", 3, 0.84
        elif NUMBERED_HEADING_PATTERN.match(text):
            level = _numbered_heading_level(text)
            kind = f"heading_{level}"  # type: ignore[assignment]
            confidence = 0.86 if level == 2 else 0.84
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
        normalized_aliases = [
            (alias.lower(), section)
            for section in rules.required_sections
            for alias in section.aliases
        ]
        kind_to_section = {
            "abstract": "Chinese Abstract",
            "toc": "Table of Contents",
            "references": "References",
            "appendix": "Appendix",
            "acknowledgements": "Acknowledgements",
        }

        for offset, block in enumerate(blocks):
            matched_names = set()
            if matched := kind_to_section.get(block.kind):
                matched_names.add(matched)

            normalized_text = block.text.lower()
            if (block.source_style or "").lower() == "bibliography":
                matched_names.add("References")
            for alias, section in normalized_aliases:
                if normalized_text == alias or (
                    block.kind in {"heading_1", "heading_2", "heading_3"}
                    and alias in normalized_text
                ):
                    matched_names.add(section.name)

            if block.kind == "heading_1" and "Body" not in sections:
                matched_names.add("Body")

            for matched in matched_names:
                if matched in sections:
                    continue
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


def _style_is_heading(lower_style: str, level: int) -> bool:
    heading_tokens = {
        1: ("heading 1", "heading1", "标题 1", "标题1", "一级"),
        2: ("heading 2", "heading2", "标题 2", "标题2", "二级"),
        3: ("heading 3", "heading3", "标题 3", "标题3", "三级"),
    }
    return any(token in lower_style for token in heading_tokens[level])


def _numbered_heading_level(text: str) -> int:
    prefix = text.split(maxsplit=1)[0]
    return min(prefix.count(".") + 1, 3)
