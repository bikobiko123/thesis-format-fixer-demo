from app.rules.loader import list_supported_degrees, load_rules


def test_loads_swufe_master_rules_from_policy_document() -> None:
    rules = load_rules("swufe_master")

    assert "swufe_master" in list_supported_degrees()
    assert rules.school == "西南财经大学"
    assert rules.degree == "master"
    assert rules.page_setup.top_cm == 3.9
    assert rules.page_setup.bottom_cm == 3.4
    assert rules.page_setup.left_cm == 3.45
    assert rules.page_setup.right_cm == 3.45
    assert rules.styles["body"].font_family == "SimSun"
    assert rules.styles["body"].font_size_pt == 12
    assert rules.styles["body"].line_spacing == 1.37
    assert rules.styles["heading_1"].font_family == "STZhongsong"
    assert rules.styles["caption"].font_size_pt == 10.5
