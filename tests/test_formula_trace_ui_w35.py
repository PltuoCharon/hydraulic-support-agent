from pathlib import Path


API = Path("web/src/api/index.js")
VIEW = Path("web/src/views/ColumnView.vue")


def api_text():
    return API.read_text(encoding="utf-8")


def view_text():
    return VIEW.read_text(encoding="utf-8")


def test_formula_detail_api_is_read_only_get():
    s = api_text()
    assert "export const getFormula" in s
    assert "http.get(`/api/formulas/${formulaId}`)" in s


def test_record_formula_id_opens_registry_detail():
    s = view_text()
    assert "@click=\"openFormulaDetail(formulaId)\"" in s
    assert "Formula Registry 详情" in s


def test_formula_detail_is_cleared_before_request():
    s = view_text()
    start = s.index("const openFormulaDetail")
    end = s.index("const designExampleIsCurrent", start)
    block = s[start:end]

    assert "formulaDetail.value = null" in block
    assert "await getFormula(formulaId)" in block
    assert block.index(
        "formulaDetail.value = null"
    ) < block.index(
        "await getFormula(formulaId)"
    )


def test_formula_dialog_uses_registry_response_fields():
    s = view_text()

    for field in (
        "formula_id",
        "module",
        "name",
        "status",
        "formula",
        "input_vars",
        "output",
        "unit",
        "source",
        "verification",
        "current_callers",
        "notes",
    ):
        assert f"formulaDetail.{field}" in s


def test_formula_status_is_displayed_without_frontend_remapping():
    s = view_text()
    assert "{{ formulaDetail.status }}" in s


def test_formula_trace_adds_no_mutation_api():
    s = api_text() + view_text()

    for symbol in (
        "postFormula",
        "putFormula",
        "patchFormula",
        "deleteFormula",
        "updateFormula",
        "saveFormula",
    ):
        assert symbol not in s
