from typing import Literal

from pydantic import BaseModel, Field


class MarginRule(BaseModel):
    top_cm: float
    bottom_cm: float
    left_cm: float
    right_cm: float
    header_cm: float | None = None
    footer_cm: float | None = None


class StyleRule(BaseModel):
    style_name: str | None = None
    font_family: str
    ascii_font_family: str | None = None
    east_asia_font_family: str | None = None
    font_size_pt: float
    bold: bool = False
    alignment: Literal["left", "center", "right", "justify"] = "left"
    line_spacing: float = 1.5
    first_line_indent_chars: float = 0
    first_line_indent_cm: float | None = None
    space_before_pt: float | None = None
    space_after_pt: float | None = None


class SectionRule(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    required: bool = True
    order: int


class PageNumberRule(BaseModel):
    enabled: bool = True
    start_at_body: bool = True
    body_format: str = "arabic"


class ThesisRules(BaseModel):
    school: str
    degree: Literal["undergraduate", "master"]
    version: str
    page_setup: MarginRule
    styles: dict[str, StyleRule]
    required_sections: list[SectionRule]
    page_numbers: PageNumberRule
    captions: dict[str, str]
    validators: list[str]
