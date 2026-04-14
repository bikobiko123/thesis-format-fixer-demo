import json
from functools import lru_cache
from pathlib import Path

from app.core.exceptions import UnsupportedDegreeError
from app.rules.schema import ThesisRules

RULE_DIR = Path(__file__).parent / "data"


@lru_cache
def load_rules(degree: str) -> ThesisRules:
    rule_file = RULE_DIR / f"{degree}.json"
    if not rule_file.exists():
        raise UnsupportedDegreeError(f"Unsupported degree: {degree}")

    with rule_file.open("r", encoding="utf-8") as handle:
        return ThesisRules.model_validate(json.load(handle))


def list_supported_degrees() -> list[str]:
    return sorted(path.stem for path in RULE_DIR.glob("*.json"))
