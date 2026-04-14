import json
import logging
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from app.ir.models import ThesisBlock
from app.llm.base import LLMProvider, StructureLabel
from app.validation.validator import ValidationItem

logger = logging.getLogger(__name__)

ALLOWED_STRUCTURE_KINDS = {
    "title",
    "abstract",
    "keywords",
    "toc",
    "heading_1",
    "heading_2",
    "body",
    "references",
    "appendix",
    "caption",
    "acknowledgements",
    "unknown",
}


class RuleBasedLLMProvider:
    """Offline fallback that keeps the MVP deterministic and runnable without API keys."""

    def propose_structure_labels(self, blocks: list[ThesisBlock]) -> dict[int, StructureLabel]:
        return {}

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


class OpenAICompatibleLLMProvider:
    """OpenAI-compatible JSON provider for structure labels and explanations.

    The provider only returns proposed labels plus explanations. Callers still use the rule
    engine to decide and execute formatting repairs.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model: str,
        timeout_seconds: int = 20,
        audit_log_path: Path | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.audit_log_path = audit_log_path

    def propose_structure_labels(self, blocks: list[ThesisBlock]) -> dict[int, StructureLabel]:
        prompt = {
            "instruction": (
                "Label thesis document blocks for formatting analysis only. "
                'Return strict JSON: {"labels":[{"index":0,"kind":"abstract",'
                '"confidence":0.7,"explanation":"..."}]}. '
                "Do not propose repairs or content changes."
            ),
            "allowed_kinds": sorted(ALLOWED_STRUCTURE_KINDS),
            "blocks": [
                {
                    "index": block.index,
                    "text": block.text[:160],
                    "current_kind": block.kind,
                    "style": block.source_style,
                }
                for block in blocks[:80]
            ],
        }
        try:
            content = self._chat_json(prompt)
            payload = json.loads(content)
        except (OSError, URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("LLM structure labeling failed; using heuristic labels: %s", exc)
            return {}

        labels: dict[int, StructureLabel] = {}
        for item in payload.get("labels", []):
            index = item.get("index")
            kind = item.get("kind")
            if not isinstance(index, int) or kind not in ALLOWED_STRUCTURE_KINDS:
                continue
            labels[index] = StructureLabel(
                kind=kind,
                explanation=str(item.get("explanation") or "LLM proposed this label."),
                confidence=float(item.get("confidence") or 0.7),
            )

        self._write_audit(blocks, labels)
        return labels

    def explain_structure(self, blocks: list[ThesisBlock]) -> dict[int, str]:
        return {
            block.index: f"LLM-backed recognizer final label: {block.kind}."
            for block in blocks
            if block.kind != "body"
        }

    def explain_validation_item(self, item: ValidationItem) -> str:
        return RuleBasedLLMProvider().explain_validation_item(item)

    def _chat_json(self, prompt: dict) -> str:
        body = json.dumps(
            {
                "model": self.model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a thesis formatting structure classifier. "
                            "You never modify thesis content and never output repairs."
                        ),
                    },
                    {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
                ],
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = Request(
            self.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
        return response_payload["choices"][0]["message"]["content"]

    def _write_audit(self, blocks: list[ThesisBlock], labels: dict[int, StructureLabel]) -> None:
        if self.audit_log_path is None:
            return
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "model": self.model,
            "input_block_count": len(blocks),
            "label_count": len(labels),
            "labels": {
                index: {
                    "kind": label.kind,
                    "confidence": label.confidence,
                    "explanation": label.explanation,
                }
                for index, label in labels.items()
            },
        }
        with self.audit_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_llm_provider(
    provider_name: str,
    api_key: str | None = None,
    endpoint: str | None = None,
    model: str = "gpt-4o-mini",
    timeout_seconds: int = 20,
    audit_log_path: Path | None = None,
) -> LLMProvider:
    if provider_name == "openai_compatible":
        if not endpoint or not api_key:
            raise ValueError(
                "openai_compatible requires THESIS_LLM_ENDPOINT and THESIS_LLM_API_KEY."
            )
        return OpenAICompatibleLLMProvider(
            endpoint=endpoint,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            audit_log_path=audit_log_path,
        )
    return RuleBasedLLMProvider()
