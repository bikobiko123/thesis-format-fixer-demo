from typing import Protocol

from app.ir.models import ThesisBlock
from app.validation.validator import ValidationItem


class LLMProvider(Protocol):
    """Provider interface for future cloud/local LLM integrations."""

    def explain_structure(self, blocks: list[ThesisBlock]) -> dict[int, str]:
        raise NotImplementedError

    def explain_validation_item(self, item: ValidationItem) -> str:
        raise NotImplementedError
