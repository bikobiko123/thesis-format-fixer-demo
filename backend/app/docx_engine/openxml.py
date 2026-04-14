import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from app.docx_engine.base import DocxDocumentInfo
from app.docx_engine.python_docx import PythonDocxEngine

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)


def _w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def _rel(tag: str) -> str:
    return f"{{{REL_NS}}}{tag}"


def _ct(tag: str) -> str:
    return f"{{{CONTENT_TYPES_NS}}}{tag}"


def _attr(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def _twips_from_cm(value: float | None) -> str | None:
    if value is None:
        return None
    return str(round(value * 567))


def _find_or_add(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    return child


class OpenXmlDocxEngine:
    """DOCX engine for OOXML-only repair operations that python-docx cannot express."""

    def __init__(self) -> None:
        self._parser = PythonDocxEngine()

    def parse(self, path: Path) -> DocxDocumentInfo:
        return self._parser.parse(path)

    def repair(self, source_path: Path, output_path: Path, operations: list[dict]) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._parser.repair(source_path, output_path, operations)

        with zipfile.ZipFile(output_path, "r") as package:
            parts = {name: package.read(name) for name in package.namelist()}
            document = ET.fromstring(parts["word/document.xml"])
            rels = ET.fromstring(parts["word/_rels/document.xml.rels"])
            content_types = ET.fromstring(parts["[Content_Types].xml"])

            changed: set[str] = set()
            footer_part = self._ensure_footer_part(parts, rels, content_types, changed)

            delayed_operations: list[dict] = []
            margin_operation: dict | None = None
            footer_operation: dict | None = None
            for operation in operations:
                op_type = operation.get("type")
                if op_type == "set_margins":
                    margin_operation = operation
                elif op_type == "ensure_page_number_footer":
                    parts[footer_part] = self._page_number_footer_xml()
                    footer_operation = operation
                    changed.update(
                        {footer_part, "word/document.xml", "word/_rels/document.xml.rels"}
                    )
                elif op_type == "ensure_section_break_before":
                    self._ensure_section_break_before(document, operation["paragraph_index"])
                    changed.add("word/document.xml")
                elif op_type == "mark_toc_dirty":
                    delayed_operations.append(operation)

            if margin_operation:
                self._set_margins(document, margin_operation["margins"])
                changed.add("word/document.xml")

            if footer_operation:
                self._ensure_footer_refs(document, rels, footer_part)
                if footer_operation.get("restart_at_body"):
                    self._restart_page_numbering(document)
                changed.update({"word/document.xml", "word/_rels/document.xml.rels"})

            for operation in delayed_operations:
                if operation.get("type") == "mark_toc_dirty":
                    self._mark_toc_dirty(document)
                    changed.add("word/document.xml")

            parts["word/document.xml"] = ET.tostring(
                document, encoding="utf-8", xml_declaration=True
            )
            parts["word/_rels/document.xml.rels"] = ET.tostring(
                rels, encoding="utf-8", xml_declaration=True
            )
            parts["[Content_Types].xml"] = ET.tostring(
                content_types, encoding="utf-8", xml_declaration=True
            )
            changed.update(
                {"word/document.xml", "word/_rels/document.xml.rels", "[Content_Types].xml"}
            )
            self._rewrite_package(output_path, package.namelist(), parts, changed)

        return output_path

    def _rewrite_package(
        self,
        output_path: Path,
        original_names: list[str],
        parts: dict[str, bytes],
        changed: set[str],
    ) -> None:
        temp_path = output_path.with_suffix(".tmp.docx")
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as target:
            seen: set[str] = set()
            for name in original_names:
                if name in seen:
                    continue
                target.writestr(name, parts[name])
                seen.add(name)
            for name in sorted(changed - seen):
                target.writestr(name, parts[name])
        temp_path.replace(output_path)

    def _set_margins(self, document: ET.Element, margins: dict) -> None:
        for sect_pr in document.findall(f".//{_w('sectPr')}"):
            pg_mar = _find_or_add(sect_pr, _w("pgMar"))
            mapping = {
                "top": _twips_from_cm(margins.get("top_cm")),
                "bottom": _twips_from_cm(margins.get("bottom_cm")),
                "left": _twips_from_cm(margins.get("left_cm")),
                "right": _twips_from_cm(margins.get("right_cm")),
                "header": _twips_from_cm(margins.get("header_cm")),
                "footer": _twips_from_cm(margins.get("footer_cm")),
            }
            for key, value in mapping.items():
                if value is not None:
                    pg_mar.set(_attr(W_NS, key), value)

    def _ensure_footer_part(
        self,
        parts: dict[str, bytes],
        rels: ET.Element,
        content_types: ET.Element,
        changed: set[str],
    ) -> str:
        existing = [
            relationship
            for relationship in rels.findall(_rel("Relationship"))
            if relationship.get("Type", "").endswith("/footer")
        ]
        if existing:
            target = existing[0].get("Target", "footer1.xml")
            return f"word/{target}"

        next_id = self._next_relationship_id(rels)
        footer_part = "word/footer1.xml"
        counter = 1
        while footer_part in parts:
            counter += 1
            footer_part = f"word/footer{counter}.xml"

        ET.SubElement(
            rels,
            _rel("Relationship"),
            {
                "Id": next_id,
                "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer",
                "Target": footer_part.removeprefix("word/"),
            },
        )
        ET.SubElement(
            content_types,
            _ct("Override"),
            {
                "PartName": f"/{footer_part}",
                "ContentType": (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
                ),
            },
        )
        parts[footer_part] = self._page_number_footer_xml()
        changed.update({footer_part, "word/_rels/document.xml.rels", "[Content_Types].xml"})
        return footer_part

    def _next_relationship_id(self, rels: ET.Element) -> str:
        ids = [
            int(value[3:])
            for relationship in rels.findall(_rel("Relationship"))
            if (value := relationship.get("Id", "")).startswith("rId") and value[3:].isdigit()
        ]
        return f"rId{max(ids, default=0) + 1}"

    def _page_number_footer_xml(self) -> bytes:
        root = ET.Element(_w("ftr"))
        paragraph = ET.SubElement(root, _w("p"))
        run = ET.SubElement(paragraph, _w("r"))
        begin = ET.SubElement(run, _w("fldChar"))
        begin.set(_attr(W_NS, "fldCharType"), "begin")
        instruction = ET.SubElement(run, _w("instrText"))
        instruction.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        instruction.text = " PAGE "
        end = ET.SubElement(run, _w("fldChar"))
        end.set(_attr(W_NS, "fldCharType"), "end")
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def _ensure_footer_refs(self, document: ET.Element, rels: ET.Element, footer_part: str) -> None:
        rel_id = next(
            relationship.get("Id")
            for relationship in rels.findall(_rel("Relationship"))
            if relationship.get("Target") == footer_part.removeprefix("word/")
        )
        for sect_pr in document.findall(f".//{_w('sectPr')}"):
            refs = sect_pr.findall(_w("footerReference"))
            if refs:
                for ref in refs:
                    ref.set(_attr(R_NS, "id"), rel_id)
            else:
                ref = ET.Element(_w("footerReference"))
                ref.set(_attr(W_NS, "type"), "default")
                ref.set(_attr(R_NS, "id"), rel_id)
                sect_pr.insert(0, ref)

    def _restart_page_numbering(self, document: ET.Element) -> None:
        body = document.find(_w("body"))
        if body is None:
            return
        sect_pr = body.find(_w("sectPr"))
        if sect_pr is None:
            sect_pr = document.find(f".//{_w('sectPr')}")
        if sect_pr is None:
            sect_pr = ET.SubElement(body, _w("sectPr"))
        pg_num_type = _find_or_add(sect_pr, _w("pgNumType"))
        pg_num_type.set(_attr(W_NS, "start"), "1")

    def _ensure_section_break_before(self, document: ET.Element, paragraph_index: int) -> None:
        paragraphs = document.findall(f".//{_w('p')}")
        if paragraph_index <= 0 or paragraph_index >= len(paragraphs):
            return
        previous = paragraphs[paragraph_index - 1]
        p_pr = _find_or_add(previous, _w("pPr"))
        sect_pr = _find_or_add(p_pr, _w("sectPr"))
        sect_type = _find_or_add(sect_pr, _w("type"))
        sect_type.set(_attr(W_NS, "val"), "nextPage")

    def _mark_toc_dirty(self, document: ET.Element) -> None:
        for instruction in document.findall(f".//{_w('instrText')}"):
            if instruction.text and "TOC" in instruction.text.upper():
                parent = self._find_parent(document, instruction)
                if parent is not None:
                    dirty = ET.Element(_w("fldChar"))
                    dirty.set(_attr(W_NS, "fldCharType"), "begin")
                    dirty.set(_attr(W_NS, "dirty"), "true")
                    parent.insert(0, dirty)
                    return

        paragraph = ET.Element(_w("p"))
        run = ET.SubElement(paragraph, _w("r"))
        begin = ET.SubElement(run, _w("fldChar"))
        begin.set(_attr(W_NS, "fldCharType"), "begin")
        begin.set(_attr(W_NS, "dirty"), "true")
        instruction = ET.SubElement(run, _w("instrText"))
        instruction.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        instruction.text = ' TOC \\o "1-3" \\h \\z \\u '
        separate = ET.SubElement(run, _w("fldChar"))
        separate.set(_attr(W_NS, "fldCharType"), "separate")
        end = ET.SubElement(run, _w("fldChar"))
        end.set(_attr(W_NS, "fldCharType"), "end")
        body = document.find(_w("body"))
        if body is not None:
            body.insert(0, paragraph)

    def _find_parent(self, root: ET.Element, needle: ET.Element) -> ET.Element | None:
        for parent in root.iter():
            if needle in list(parent):
                return parent
        return None
