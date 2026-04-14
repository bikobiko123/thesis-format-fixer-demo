from dataclasses import replace

from app.docx_engine.base import DocxDocumentInfo
from app.ir.models import ThesisDocument
from app.llm.base import LLMProvider
from app.rules.schema import ThesisRules
from app.structure.recognizer import HeuristicStructureRecognizer


class LLMStructureRecognizer:
    """LLM-assisted recognizer that only labels/explains structure, never repairs."""

    def __init__(
        self, base_recognizer: HeuristicStructureRecognizer, llm_provider: LLMProvider
    ) -> None:
        self.base_recognizer = base_recognizer
        self.llm_provider = llm_provider

    def recognize(self, doc: DocxDocumentInfo, rules: ThesisRules) -> ThesisDocument:
        base_ir = self.base_recognizer.recognize(doc, rules)
        proposals = self.llm_provider.propose_structure_labels(base_ir.blocks)
        if not proposals:
            return base_ir

        blocks = []
        for block in base_ir.blocks:
            proposal = proposals.get(block.index)
            if proposal is None:
                blocks.append(block)
                continue
            blocks.append(
                replace(
                    block,
                    kind=proposal.kind,
                    confidence=proposal.confidence,
                    notes=[*block.notes, proposal.explanation],
                )
            )

        sections = self.base_recognizer._build_sections(blocks, rules)
        return replace(base_ir, blocks=blocks, sections=sections)
