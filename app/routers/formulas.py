from fastapi import APIRouter

from app.services.formula_registry import (
    FormulaRegistryDataError,
    get_formula,
    list_formulas,
)


router = APIRouter(prefix="/formulas")


@router.get("")
def formula_list():
    try:
        return {
            "code": 0,
            "data": list_formulas(),
        }
    except FormulaRegistryDataError as exc:
        return {
            "code": 1,
            "msg": str(exc),
        }


@router.get("/{formula_id}")
def formula_detail(formula_id: str):
    try:
        row = get_formula(formula_id)

        if row is None:
            return {
                "code": 1,
                "msg": "formula not found",
            }

        return {
            "code": 0,
            "data": row,
        }

    except (
        ValueError,
        FormulaRegistryDataError,
    ) as exc:
        return {
            "code": 1,
            "msg": str(exc),
        }
