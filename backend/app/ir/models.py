from dataclasses import dataclass, field
from typing import Literal

BlockKind = Literal[
    "title",
    "abstract",
    "keywords",
    "toc",
    "heading_1",
    "heading_2",
    "heading_3",
    "body",
    "references",
    "appendix",
    "caption",
    "acknowledgements",
    "unknown",
]


@dataclass(frozen=True)
class ThesisBlock:
    index: int
    text: str
    kind: BlockKind
    source_style: str | None = None
    heading_level: int | None = None
    confidence: float = 1.0
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ThesisSection:
    name: str
    start_block: int
    end_block: int | None = None
    required: bool = True


@dataclass(frozen=True)
class ThesisDocument:
    degree: str
    blocks: list[ThesisBlock]
    sections: dict[str, ThesisSection]
    metadata: dict[str, str] = field(default_factory=dict)
