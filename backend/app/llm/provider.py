from app.ir.models import ThesisBlock
from app.llm.base import LLMProvider
from app.validation.validator import ValidationItem


class RuleBasedLLMProvider:
    """Offline fallback that keeps the MVP deterministic and runnable without API keys."""

    def explain_structure(self, blocks: list[ThesisBlock]) -> dict[int, str]:
        return {
            block.index: f"Detected as {block.kind} with confidence {block.confidence:.2f}."
            for block in blocks
            if block.kind != "body"
        }

    def explain_validation_item(self, item: ValidationItem) -> str:
        if item.status == "fail":
            return f"This must be fixed before submission: {item.message}"
        if item.status == "warn":
            return f"This needs manual confirmation: {item.message}"
        return item.message


def build_llm_provider(provider_name: str, api_key: str | None = None) -> LLMProvider:
    if provider_name != "rule_based" and not api_key:
        raise ValueError("Non-rule-based LLM providers require THESIS_LLM_API_KEY.")
    return RuleBasedLLMProvider()
