from pathlib import Path

from app.docx_engine.openxml import OpenXmlDocxEngine
from app.llm.provider import OpenAICompatibleLLMProvider, RuleBasedLLMProvider
from app.services.factory import build_docx_engine, build_structure_recognizer
from app.structure.llm_recognizer import LLMStructureRecognizer


def test_build_docx_engine_selects_openxml_and_python_docx() -> None:
    assert isinstance(build_docx_engine("openxml"), OpenXmlDocxEngine)
    assert build_docx_engine("python_docx").__class__.__name__ == "PythonDocxEngine"


def test_build_structure_recognizer_wraps_base_when_llm_enabled() -> None:
    recognizer = build_structure_recognizer("llm", RuleBasedLLMProvider())

    assert isinstance(recognizer, LLMStructureRecognizer)


def test_openai_compatible_provider_can_be_constructed_without_network() -> None:
    provider = OpenAICompatibleLLMProvider(
        endpoint="https://example.invalid/v1/chat/completions",
        api_key="test-key",
        model="demo-model",
        timeout_seconds=1,
        audit_log_path=Path("/tmp/thesis-llm-audit.jsonl"),
    )

    assert provider.model == "demo-model"
