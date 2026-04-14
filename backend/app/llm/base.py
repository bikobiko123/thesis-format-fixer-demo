from dataclasses import dataclass
from typing import Protocol

from app.ir.models import BlockKind, ThesisBlock
from app.validation.validator import ValidationItem


@dataclass(frozen=True)
class StructureLabel:
    kind: BlockKind
    explanation: str
    confidence: float = 0.7


class LLMProvider(Protocol):
    """Provider interface for future cloud/local LLM integrations."""

    def propose_structure_labels(self, blocks: list[ThesisBlock]) -> dict[int, StructureLabel]:
        raise NotImplementedError

    def explain_structure(self, blocks: list[ThesisBlock]) -> dict[int, str]:
        raise NotImplementedError

    def explain_validation_item(self, item: ValidationItem) -> str:
        raise NotImplementedError
