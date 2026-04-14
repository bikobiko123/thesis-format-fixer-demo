from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ParagraphInfo:
    index: int
    text: str
    style_name: str | None = None
    alignment: str | None = None
    font_name: str | None = None
    font_size_pt: float | None = None
    is_bold: bool | None = None


@dataclass(frozen=True)
class SectionInfo:
    index: int
    top_margin_cm: float | None = None
    bottom_margin_cm: float | None = None
    left_margin_cm: float | None = None
    right_margin_cm: float | None = None
    header_distance_cm: float | None = None
    footer_distance_cm: float | None = None


@dataclass(frozen=True)
class HeaderFooterInfo:
    section_index: int
    kind: str
    text: str


@dataclass(frozen=True)
class DocxDocumentInfo:
    paragraphs: list[ParagraphInfo] = field(default_factory=list)
    sections: list[SectionInfo] = field(default_factory=list)
    headers: list[HeaderFooterInfo] = field(default_factory=list)
    footers: list[HeaderFooterInfo] = field(default_factory=list)
    has_toc_field: bool = False
    toc_needs_update: bool = False


class DocxEngine(Protocol):
    """Interface reserved for future replacement with a lower-level Open XML engine."""

    def parse(self, path: Path) -> DocxDocumentInfo:
        raise NotImplementedError

    def repair(self, source_path: Path, output_path: Path, operations: list[dict]) -> Path:
        raise NotImplementedError
