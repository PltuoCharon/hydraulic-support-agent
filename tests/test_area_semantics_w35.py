from pathlib import Path


ROOT = Path("docs/evidence/w35")


def test_legacy_canopy_rule_is_deprecated():
    s = Path("docs/控顶长度估算规则.md").read_text(
        encoding="utf-8"
    )

    assert "DEPRECATED FOR NEW DESIGN CHAIN" in s
    assert "不得直接等同于控顶宽度" in s
    assert "W25" in s


def test_w35d2_uses_explicit_control_width():
    s = (
        ROOT / "W35D2_支护面积与阻力换算裁定.md"
    ).read_text(encoding="utf-8")

    assert "control_width_m" in s
    assert "explicit_design_input" in s

    assert (
        "A_control = B × B_c"
        in s
    )

    assert (
        "F_base = q_need_mpa × A_control_m2 × 1000"
        in s
    )


def test_old_area_semantics_stay_legacy():
    s = (
        ROOT / "W35D2_支护面积与阻力换算裁定.md"
    ).read_text(encoding="utf-8")

    assert "F-LEG-002" in s
    assert "F-SC-003" in s
    assert "legacy_review" in s

    assert (
        "不得从现有 `canopy_len` 静默转换"
        in s
    )


def test_new_formulas_are_active_after_validation():
    s = (
        ROOT / "W35D2_支护面积与阻力换算裁定.md"
    ).read_text(encoding="utf-8")

    assert "## 15. W35D2 最终冻结状态" in s
    assert "`F-QN-005`：active" in s
    assert "`F-QN-006`：active" in s
    assert "`F-QN-007`：active" in s
    assert "标准并不直接定义项目的" in s


def test_w35d2_support_efficiency_is_separate():
    s = (
        ROOT / "W35D2_支护面积与阻力换算裁定.md"
    ).read_text(encoding="utf-8")

    assert "F-QN-007" in s
    assert "F_rated = F_base / support_efficiency" in s
    assert "support_efficiency = K_s" in s
    assert "eta != K_s" in s
    assert "safety_factor = 1.2" in s
    assert "不得使用单一固定默认值" in s


def test_w35d2_standard_evidence_exists():
    s = (
        ROOT / "W35D2_标准证据.md"
    ).read_text(encoding="utf-8")

    assert "KA/T 554-1996" in s
    assert "KA/T 556-1996" in s
    assert "F_s = P_s × S_c × B_c / K_s" in s
    assert "eta == K_s" in s
    assert "不得直接等价" in s
