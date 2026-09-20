import json
from copy import deepcopy

from app.db import get_conn


ALLOWED_RUN_MODES = {"engineering", "example"}
ALLOWED_CONTEXT_SOURCES = {
    "selected_support",
    "calculated_requirement",
    "user_input",
}


def _json_text(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def normalize_context(
    *,
    p_kn,
    run_mode,
    context_source_type=None,
    context_confirmed=None,
    context_snapshot=None,
):
    if run_mode not in ALLOWED_RUN_MODES:
        raise ValueError("unsupported run_mode")

    if context_source_type is not None:
        if context_source_type not in ALLOWED_CONTEXT_SOURCES:
            raise ValueError("unsupported context_source_type")

    if run_mode == "example":
        return None, None, context_snapshot

    if context_source_type is None:
        return "user_input", None, context_snapshot

    if context_source_type == "user_input":
        return "user_input", None, context_snapshot

    if context_confirmed is not True:
        raise ValueError("transferred design context is not confirmed")

    snapshot = deepcopy(context_snapshot) if context_snapshot else {}
    target = snapshot.get("target") or {}
    reference = target.get("resistance_kn")

    if reference is None:
        raise ValueError("transferred design context lacks resistance_kn")

    try:
        reference_value = float(reference)
        actual_value = float(p_kn)
    except (TypeError, ValueError):
        raise ValueError("invalid transferred resistance_kn") from None

    if abs(reference_value - actual_value) > 1e-9:
        snapshot["actual_input_override"] = {
            "field": "p_kn",
            "reference_value": reference_value,
            "actual_value": actual_value,
        }
        return "user_input", None, snapshot

    return context_source_type, True, snapshot


def create_calculation_record(
    *,
    calc_type,
    run_mode,
    formula_ids,
    inputs_snapshot,
    outputs_snapshot,
    context_source_type=None,
    context_confirmed=None,
    context_snapshot=None,
):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO calculation_records (
                    record_version,
                    calc_type,
                    run_mode,
                    formula_ids,
                    inputs_snapshot,
                    outputs_snapshot,
                    context_source_type,
                    context_confirmed,
                    context_snapshot
                )
                VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    calc_type,
                    run_mode,
                    _json_text(formula_ids),
                    _json_text(inputs_snapshot),
                    _json_text(outputs_snapshot),
                    context_source_type,
                    context_confirmed,
                    (
                        _json_text(context_snapshot)
                        if context_snapshot is not None
                        else None
                    ),
                ),
            )
            record_id = cur.lastrowid
        conn.commit()
        return record_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
