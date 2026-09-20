import json
from copy import deepcopy

from app.db import get_conn


ALLOWED_RUN_MODES = {"engineering", "example"}
ALLOWED_CALC_TYPES = {"column_design"}


class CalculationRecordDataError(ValueError):
    pass
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
        return None, None, None

    if context_source_type is None:
        return "user_input", None, None

    if context_source_type == "user_input":
        return "user_input", None, None

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


def _decode_json_field(raw, field_name, expected_type, allow_none=False):
    if raw is None:
        if allow_none:
            return None
        raise CalculationRecordDataError(
            f"{field_name} must not be NULL"
        )

    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise CalculationRecordDataError(
            f"invalid JSON in {field_name}"
        ) from exc

    if not isinstance(value, expected_type):
        raise CalculationRecordDataError(
            f"invalid top-level type in {field_name}"
        )

    return value


def _normalize_context_confirmed(value):
    if value is None:
        return None
    if value not in (0, 1, False, True):
        raise CalculationRecordDataError(
            "invalid context_confirmed"
        )
    return bool(value)


def _normalize_record_row(row, include_snapshots):
    if row is None:
        return None

    data = dict(row)
    data["formula_ids"] = _decode_json_field(
        data.get("formula_ids"),
        "formula_ids",
        list,
    )
    data["context_confirmed"] = _normalize_context_confirmed(
        data.get("context_confirmed")
    )

    if include_snapshots:
        data["inputs_snapshot"] = _decode_json_field(
            data.get("inputs_snapshot"),
            "inputs_snapshot",
            dict,
        )
        data["outputs_snapshot"] = _decode_json_field(
            data.get("outputs_snapshot"),
            "outputs_snapshot",
            dict,
        )
        data["context_snapshot"] = _decode_json_field(
            data.get("context_snapshot"),
            "context_snapshot",
            dict,
            allow_none=True,
        )

    return data


def list_calculation_records(calc_type="column_design", limit=20):
    if calc_type not in ALLOWED_CALC_TYPES:
        raise ValueError("unsupported calc_type")

    if (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or not 1 <= limit <= 100
    ):
        raise ValueError("limit must be an integer between 1 and 100")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    record_version,
                    calc_type,
                    run_mode,
                    formula_ids,
                    context_source_type,
                    context_confirmed,
                    created_at
                FROM calculation_records
                WHERE calc_type = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s
                """,
                (calc_type, limit),
            )
            rows = cur.fetchall()

        return [
            _normalize_record_row(
                row,
                include_snapshots=False,
            )
            for row in rows
        ]
    finally:
        conn.close()


def get_calculation_record(record_id):
    if (
        not isinstance(record_id, int)
        or isinstance(record_id, bool)
        or record_id <= 0
    ):
        raise ValueError("record_id must be a positive integer")

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    record_version,
                    calc_type,
                    run_mode,
                    formula_ids,
                    inputs_snapshot,
                    outputs_snapshot,
                    context_source_type,
                    context_confirmed,
                    context_snapshot,
                    created_at
                FROM calculation_records
                WHERE id = %s
                LIMIT 1
                """,
                (record_id,),
            )
            row = cur.fetchone()

        return _normalize_record_row(
            row,
            include_snapshots=True,
        )
    finally:
        conn.close()
