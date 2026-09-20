import csv
import inspect
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.routers.calc import ColumnDesignReq
from app.services.calc.column import SOURCE, bore_diameter, design


COLUMN = Path("app/services/calc/column.py")
VIEW = Path("web/src/views/ColumnView.vue")
REGISTRY = Path("docs/evidence/formulas/W34D2_Formula_Registry.csv")


def test_eta_has_no_implicit_default_in_active_column_design():
    assert inspect.signature(bore_diameter).parameters["eta"].default is inspect._empty
    assert inspect.signature(design).parameters["eta"].default is inspect._empty


def test_column_design_api_requires_explicit_eta():
    with pytest.raises(ValidationError):
        ColumnDesignReq(
            p_kn=2533,
            n=1,
            p_mpa=31.5,
        )


def test_column_source_separates_bore_standard_from_project_relation():
    assert "GB/T 2348" in SOURCE
    assert "\u9879\u76ee\u7acb\u67f1\u53c2\u6570\u5316\u8ba1\u7b97\u5f0f" in SOURCE
    assert "\u7269\u7406\u53e3\u5f84\u5f85\u6838" in SOURCE


def test_eta_range_is_interface_boundary_not_common_rule():
    s = COLUMN.read_text(encoding="utf-8")
    assert "\u5386\u53f2\u7acb\u67f1\u4fee\u6b63\u7cfb\u6570 eta=" in s
    assert "\u5f53\u524d\u63a5\u53e3\u5141\u8bb8\u8303\u56f4 0.8~1.0" in s
    assert "\u6548\u7387 eta=" not in s


def test_column_ui_uses_d5_canonical_labels():
    s = VIEW.read_text(encoding="utf-8")
    assert 'label="\u7acb\u67f1\u5de5\u4f5c\u538b\u529b"' in s
    assert 'label="\u5386\u53f2\u4fee\u6b63\u7cfb\u6570 \u03b7\uff08\u5f85\u6838\uff09"' in s
    assert 'label="\u5706\u6574\u540e\u8ba1\u7b97\u627f\u8f7d\u529b"' in s
    assert 'label="\u5706\u6574\u540e\u5b9e\u9645\u627f\u8f7d\u529b"' not in s


def test_formula_registry_records_d5_column_evidence_boundaries():
    with REGISTRY.open(encoding="utf-8", newline="") as f:
        rows = {
            r["formula_id"]: r
            for r in csv.DictReader(f)
        }

    f1 = rows["F-COL-001"]
    assert "GB/T 2348\u4ec5\u7528\u4e8e\u6807\u51c6\u7f38\u5f84\u7cfb\u5217" in f1["source"]
    assert "eta\u987b\u663e\u5f0f\u8f93\u5165" in f1["notes"]
    assert "\u4e0d\u5f97\u7b49\u540cKs" in f1["notes"]

    f2 = rows["F-COL-002"]
    assert "\u516c\u5f0f\u672c\u8eab\u4e0d\u542beta" in f2["notes"]

    f3 = rows["F-COL-003"]
    assert "W35-D2\u5df2\u6838\u6807\u51c6\u8bc1\u636e" in f3["source"]
    assert "60%~85%" in f3["verification"]
