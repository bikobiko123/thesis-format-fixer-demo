from app.rules.loader import list_supported_degrees, load_rules


def test_loads_undergraduate_and_master_rule_sets() -> None:
    assert list_supported_degrees() == ["master", "swufe_master", "undergraduate"]
    assert load_rules("undergraduate").degree == "undergraduate"
    assert load_rules("master").page_setup.left_cm > load_rules("undergraduate").page_setup.left_cm
