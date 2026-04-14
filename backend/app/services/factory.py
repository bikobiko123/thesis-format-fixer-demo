from app.docx_engine.base import DocxEngine
from app.docx_engine.openxml import OpenXmlDocxEngine
from app.docx_engine.python_docx import PythonDocxEngine
from app.llm.base import LLMProvider
from app.structure.llm_recognizer import LLMStructureRecognizer
from app.structure.recognizer import HeuristicStructureRecognizer


def build_docx_engine(engine_name: str) -> DocxEngine:
    if engine_name == "python_docx":
        return PythonDocxEngine()
    if engine_name == "openxml":
        return OpenXmlDocxEngine()
    raise ValueError(f"Unsupported DOCX engine: {engine_name}")


def build_structure_recognizer(
    recognizer_name: str, llm_provider: LLMProvider
) -> HeuristicStructureRecognizer | LLMStructureRecognizer:
    base = HeuristicStructureRecognizer()
    if recognizer_name == "heuristic":
        return base
    if recognizer_name == "llm":
        return LLMStructureRecognizer(base, llm_provider)
    raise ValueError(f"Unsupported structure recognizer: {recognizer_name}")
