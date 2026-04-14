from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from app.docx_engine.base import (
    DocxDocumentInfo,
    HeaderFooterInfo,
    ParagraphInfo,
    SectionInfo,
)

ALIGNMENT_TO_DOCX = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def _cm(value) -> float | None:
    return round(value.cm, 2) if value is not None else None


def _paragraph_font(paragraph) -> tuple[str | None, float | None, bool | None]:
    first_run = paragraph.runs[0] if paragraph.runs else None
    if not first_run:
        return None, None, None
    font_name = first_run.font.name
    size = round(first_run.font.size.pt, 2) if first_run.font.size else None
    return font_name, size, first_run.bold


def _add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr_text)
    run._r.append(fld_char_end)


class PythonDocxEngine:
    """MVP DOCX engine backed by python-docx."""

    def parse(self, path: Path) -> DocxDocumentInfo:
        document = Document(path)
        paragraphs: list[ParagraphInfo] = []
        for index, paragraph in enumerate(document.paragraphs):
            font_name, size, bold = _paragraph_font(paragraph)
            paragraphs.append(
                ParagraphInfo(
                    index=index,
                    text=paragraph.text.strip(),
                    style_name=paragraph.style.name if paragraph.style else None,
                    alignment=str(paragraph.alignment) if paragraph.alignment is not None else None,
                    font_name=font_name,
                    font_size_pt=size,
                    is_bold=bold,
                )
            )

        sections: list[SectionInfo] = []
        headers: list[HeaderFooterInfo] = []
        footers: list[HeaderFooterInfo] = []
        for index, section in enumerate(document.sections):
            sections.append(
                SectionInfo(
                    index=index,
                    top_margin_cm=_cm(section.top_margin),
                    bottom_margin_cm=_cm(section.bottom_margin),
                    left_margin_cm=_cm(section.left_margin),
                    right_margin_cm=_cm(section.right_margin),
                    header_distance_cm=_cm(section.header_distance),
                    footer_distance_cm=_cm(section.footer_distance),
                )
            )
            headers.append(HeaderFooterInfo(index, "header", section.header.paragraphs[0].text))
            footers.append(HeaderFooterInfo(index, "footer", section.footer.paragraphs[0].text))

        return DocxDocumentInfo(
            paragraphs=paragraphs, sections=sections, headers=headers, footers=footers
        )

    def repair(self, source_path: Path, output_path: Path, operations: list[dict]) -> Path:
        document = Document(source_path)

        for operation in operations:
            op_type = operation.get("type")
            if op_type == "set_margins":
                margins = operation["margins"]
                for section in document.sections:
                    section.top_margin = Cm(margins["top_cm"])
                    section.bottom_margin = Cm(margins["bottom_cm"])
                    section.left_margin = Cm(margins["left_cm"])
                    section.right_margin = Cm(margins["right_cm"])
            elif op_type == "set_paragraph_style":
                index = operation["paragraph_index"]
                if index >= len(document.paragraphs):
                    continue
                paragraph = document.paragraphs[index]
                style = operation["style"]
                paragraph.alignment = ALIGNMENT_TO_DOCX.get(style["alignment"])
                fmt = paragraph.paragraph_format
                fmt.line_spacing = style["line_spacing"]
                fmt.first_line_indent = Cm(style["first_line_indent_chars"] * 0.37)
                for run in paragraph.runs or [paragraph.add_run()]:
                    run.font.name = style["font_family"]
                    run._element.rPr.rFonts.set(qn("w:eastAsia"), style["font_family"])
                    run.font.size = Pt(style["font_size_pt"])
                    run.bold = style["bold"]
            elif op_type == "ensure_page_number_footer":
                for section in document.sections:
                    paragraph = section.footer.paragraphs[0]
                    if "PAGE" not in paragraph._p.xml:
                        paragraph.clear()
                        _add_page_number(paragraph)
            elif op_type == "ensure_header_text":
                text = operation["text"]
                for section in document.sections:
                    paragraph = section.header.paragraphs[0]
                    if not paragraph.text.strip():
                        paragraph.text = text

        output_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(output_path)
        return output_path
