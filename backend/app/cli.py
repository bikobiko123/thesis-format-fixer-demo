import argparse
import json
import shutil
from pathlib import Path

from app.llm.provider import build_llm_provider
from app.services.factory import build_docx_engine, build_structure_recognizer
from app.services.processor import ThesisProcessor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="thesis-fix",
        description="Repair DOCX thesis formatting and write agent-friendly artifacts.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    repair = subcommands.add_parser("repair", help="Repair a DOCX thesis.")
    repair.add_argument("--input", required=True, type=Path, help="Input .docx thesis path.")
    repair.add_argument("--profile", default="swufe_master", help="Rule profile name.")
    repair.add_argument("--out", required=True, type=Path, help="Output directory.")
    repair.add_argument("--docx-engine", default="openxml", choices=["openxml", "python_docx"])
    repair.add_argument("--structure-recognizer", default="heuristic", choices=["heuristic", "llm"])
    repair.add_argument(
        "--llm-provider",
        default="rule_based",
        choices=["rule_based", "openai_compatible"],
    )
    repair.add_argument("--llm-endpoint", default=None)
    repair.add_argument("--llm-api-key", default=None)
    repair.add_argument("--llm-model", default="gpt-4o-mini")
    return parser


def repair_command(args: argparse.Namespace) -> dict:
    args.out.mkdir(parents=True, exist_ok=True)
    work_dir = args.out / ".work"
    provider = build_llm_provider(
        provider_name=args.llm_provider,
        api_key=args.llm_api_key,
        endpoint=args.llm_endpoint,
        model=args.llm_model,
        audit_log_path=args.out / "llm_structure_audit.jsonl",
    )
    processor = ThesisProcessor(
        build_docx_engine(args.docx_engine),
        provider,
        work_dir,
        recognizer=build_structure_recognizer(args.structure_recognizer, provider),
    )
    result = processor.process(args.input, args.profile)

    outputs = {
        "repaired_docx": args.out / "repaired_thesis.docx",
        "report_json": args.out / "format_report.json",
        "report_markdown": args.out / "format_report.md",
        "manual_fix_list": args.out / "manual_fix_list.md",
        "archive": args.out / "thesis_format_fix_result.zip",
    }
    shutil.copyfile(result.repaired_docx, outputs["repaired_docx"])
    shutil.copyfile(result.report_json, outputs["report_json"])
    shutil.copyfile(result.report_markdown, outputs["report_markdown"])
    shutil.copyfile(result.manual_fix_list, outputs["manual_fix_list"])
    shutil.copyfile(result.archive_path, outputs["archive"])

    return {
        "status": "ok",
        "profile": args.profile,
        "docx_engine": args.docx_engine,
        "structure_recognizer": args.structure_recognizer,
        "outputs": {key: str(path) for key, path in outputs.items()},
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "repair":
        print(json.dumps(repair_command(args), ensure_ascii=False, indent=2))
        return 0
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
