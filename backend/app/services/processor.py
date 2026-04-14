import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.core.exceptions import InvalidDocumentError
from app.docx_engine.base import DocxEngine
from app.llm.base import LLMProvider
from app.repair.engine import RuleBasedRepairPlanner
from app.reports.generator import ReportGenerator
from app.rules.loader import load_rules
from app.structure.recognizer import HeuristicStructureRecognizer
from app.validation.validator import ThesisValidator


@dataclass(frozen=True)
class ProcessedThesis:
    work_dir: Path
    repaired_docx: Path
    report_json: Path
    report_markdown: Path
    manual_fix_list: Path
    archive_path: Path


class ThesisProcessor:
    def __init__(
        self,
        docx_engine: DocxEngine,
        llm_provider: LLMProvider,
        storage_dir: Path,
        recognizer: HeuristicStructureRecognizer | None = None,
    ) -> None:
        self.docx_engine = docx_engine
        self.llm_provider = llm_provider
        self.storage_dir = storage_dir
        self.recognizer = recognizer or HeuristicStructureRecognizer()
        self.repair_planner = RuleBasedRepairPlanner()
        self.validator = ThesisValidator()
        self.report_generator = ReportGenerator()

    def process(self, source_path: Path, degree: str) -> ProcessedThesis:
        if source_path.suffix.lower() != ".docx":
            raise InvalidDocumentError("Only .docx files are supported.")

        rules = load_rules(degree)
        work_dir = self.storage_dir / uuid4().hex
        work_dir.mkdir(parents=True, exist_ok=True)

        safe_input = work_dir / "input.docx"
        shutil.copyfile(source_path, safe_input)

        source_info = self.docx_engine.parse(safe_input)
        ir = self.recognizer.recognize(source_info, rules)
        repair_plan = self.repair_planner.plan(ir, rules)
        repaired_docx = work_dir / "repaired_thesis.docx"
        self.docx_engine.repair(safe_input, repaired_docx, repair_plan.operations)

        repaired_info = self.docx_engine.parse(repaired_docx)
        repaired_ir = self.recognizer.recognize(repaired_info, rules)
        validation = self.validator.validate(repaired_ir, rules)
        explanations = self.llm_provider.explain_structure(repaired_ir.blocks)
        reports = self.report_generator.write_reports(
            work_dir,
            repaired_ir,
            validation,
            repair_plan,
            explanations,
        )

        archive_path = work_dir / "thesis_format_fix_result.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(repaired_docx, arcname="repaired_thesis.docx")
            archive.write(reports["json"], arcname="format_report.json")
            archive.write(reports["markdown"], arcname="format_report.md")
            archive.write(reports["manual"], arcname="manual_fix_list.md")

        return ProcessedThesis(
            work_dir=work_dir,
            repaired_docx=repaired_docx,
            report_json=reports["json"],
            report_markdown=reports["markdown"],
            manual_fix_list=reports["manual"],
            archive_path=archive_path,
        )
