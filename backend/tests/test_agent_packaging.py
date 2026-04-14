import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_agent_skill_and_plugin_are_packaged_without_placeholders() -> None:
    skill = ROOT / "skills" / "thesis-format-fixer" / "SKILL.md"
    plugin_skill = (
        ROOT / "plugins" / "thesis-format-fixer" / "skills" / "thesis-format-fixer" / "SKILL.md"
    )
    plugin_manifest = ROOT / "plugins" / "thesis-format-fixer" / ".codex-plugin" / "plugin.json"
    marketplace = ROOT / ".agents" / "plugins" / "marketplace.json"
    claude_command = ROOT / ".claude" / "commands" / "thesis-fix.md"

    for path in [skill, plugin_skill, plugin_manifest, marketplace, claude_command]:
        assert path.exists(), f"{path} should be present for agent-first distribution"
        assert "[TODO:" not in path.read_text(encoding="utf-8")

    skill_text = skill.read_text(encoding="utf-8")
    assert "Never generate, rewrite, summarize" in skill_text
    assert "python3.12 -m app.cli repair" in skill_text

    manifest = json.loads(plugin_manifest.read_text(encoding="utf-8"))
    assert manifest["name"] == "thesis-format-fixer"
    assert manifest["skills"] == "./skills/"
    assert "thesis formatting" in manifest["description"].lower()

    marketplace_json = json.loads(marketplace.read_text(encoding="utf-8"))
    assert marketplace_json["plugins"][0]["source"]["path"] == "./plugins/thesis-format-fixer"

    assert "python3.12 -m app.cli repair" in claude_command.read_text(encoding="utf-8")
