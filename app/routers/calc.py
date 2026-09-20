"""设计计算路由 —— W33

契约：
- docs/接口契约_W28.md 附录C：支护需求估算
- docs/接口契约_W28.md 附录D：立柱设计与强度校核

原则：
路由层只做参数接收、流程编排和统一响应；
所有物理公式均调用 app/services/calc 下的纯计算内核。
"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.calc.q_need import estimate
from app.services.calc.column import design as column_design_core
from app.services.calc.column_strength import (
    MATERIALS,
    SOURCE_WALL,
    allowable_stress,
    wall_thickness,
    check_stress,
    euler_buckling,
)

from app.services.calculation_records import (
    CalculationRecordDataError,
    create_calculation_record,
    get_calculation_record,
    list_calculation_records,
    normalize_context,
)

router = APIRouter()


# ============================================================
# W33-D2：支护需求
# ============================================================

class QNeedReq(BaseModel):
    hm: float = Field(..., description="采高 m")
    l1: float = Field(..., description="老顶初次来压步距 m")
    lp: float = Field(..., description="基本顶周期来压步距 m")
    bc: float = Field(..., description="控顶宽度 m")
    n: float = Field(..., description="直接顶充填系数 N（直接顶厚度/采高）")
    gamma: float = Field(25.0, description="顶板岩层容重 kN/m³")
    k1: float = Field(6.0, description="影响系数(6~8倍采高岩柱)")
    k: float = Field(2.0, description="动载荷系数")


@router.post("/q-need")
def q_need(req: QNeedReq):
    try:
        data = estimate(
            req.hm,
            req.l1,
            req.lp,
            req.bc,
            req.n,
            req.gamma,
            req.k1,
            req.k,
        )
        return {"code": 0, "data": data}
    except ValueError as e:
        return {"code": 1, "msg": str(e)}


# ============================================================
# W33-D5：立柱缸径设计
# ============================================================

class ColumnDesignReq(BaseModel):
    p_kn: float = Field(..., description="支架设计工作阻力 kN")
    n: int = Field(..., description="承载立柱根数")
    p_mpa: float = Field(..., description="立柱工作压力 MPa")
    eta: float = Field(..., description="历史立柱修正系数 η（物理口径待核；须显式输入）")
    p_set_kn: Optional[float] = Field(
        None,
        description="初撑力 kN；为空则不做初撑力比校核",
    )

    run_mode: str = "engineering"
    context_source_type: Optional[str] = None
    context_confirmed: Optional[bool] = None
    context_snapshot: Optional[dict] = None


@router.post("/column-design")
def column_design(req: ColumnDesignReq):
    try:
        # 这里只做请求级输入完整性检查，不重复任何物理公式。
        if req.p_set_kn is not None and not 0 <= req.p_set_kn <= 50000:
            raise ValueError(
                f"初撑力 {req.p_set_kn}kN 超出接口允许范围 0~50000kN"
            )

        data = column_design_core(
            p_kn=req.p_kn,
            n=req.n,
            p_mpa=req.p_mpa,
            eta=req.eta,
            p_set_kn=req.p_set_kn,
        )

        context_source_type, context_confirmed, context_snapshot = normalize_context(
            p_kn=req.p_kn,
            run_mode=req.run_mode,
            context_source_type=req.context_source_type,
            context_confirmed=req.context_confirmed,
            context_snapshot=req.context_snapshot,
        )

        formula_ids = [
            "F-COL-001",
            "F-COL-002",
        ]
        if req.p_set_kn is not None:
            formula_ids.append("F-COL-003")

        inputs_snapshot = {
            "p_kn": req.p_kn,
            "n": req.n,
            "p_mpa": req.p_mpa,
            "eta": req.eta,
            "p_set_kn": req.p_set_kn,
        }

        record_id = create_calculation_record(
            calc_type="column_design",
            run_mode=req.run_mode,
            formula_ids=formula_ids,
            inputs_snapshot=inputs_snapshot,
            outputs_snapshot=data,
            context_source_type=context_source_type,
            context_confirmed=context_confirmed,
            context_snapshot=context_snapshot,
        )

        data = dict(data)
        data["record_id"] = record_id

        return {"code": 0, "data": data}

    except ValueError as e:
        return {"code": 1, "msg": str(e)}


# ============================================================
# W35-D6：计算记录只读查询
# ============================================================

def _serialize_calculation_record(record):
    if record is None:
        return None

    data = dict(record)
    created_at = data.get("created_at")

    if created_at is not None:
        if not hasattr(created_at, "isoformat"):
            raise CalculationRecordDataError(
                "invalid created_at in calculation record"
            )
        data["created_at"] = created_at.isoformat()

    return data


@router.get("/records")
def calculation_records(
    calc_type: str = "column_design",
    limit: int = 20,
):
    try:
        rows = list_calculation_records(
            calc_type=calc_type,
            limit=limit,
        )
        return {
            "code": 0,
            "data": [
                _serialize_calculation_record(row)
                for row in rows
            ],
        }
    except (ValueError, CalculationRecordDataError) as e:
        return {"code": 1, "msg": str(e)}


@router.get("/records/{record_id}")
def calculation_record_detail(record_id: int):
    try:
        row = get_calculation_record(record_id)

        if row is None:
            return {
                "code": 1,
                "msg": "calculation record not found",
            }

        return {
            "code": 0,
            "data": _serialize_calculation_record(row),
        }
    except (ValueError, CalculationRecordDataError) as e:
        return {"code": 1, "msg": str(e)}


# ============================================================
# W33-D5：立柱强度校核
# ============================================================

class ColumnStrengthReq(BaseModel):
    d_mm: float = Field(..., description="缸筒内径 mm")
    p_mpa: float = Field(..., description="计算压力 MPa")

    material: str = Field(
        "27SiMn",
        description="缸筒材料；当前开放已核实材料27SiMn",
    )
    material_safety_factor: float = Field(
        2.0,
        description="计算许用应力采用的安全系数",
    )

    sigma_max_mpa: Optional[float] = Field(
        None,
        description="最大计算应力 MPa；为空则不执行应力校核",
    )

    e_mpa: Optional[float] = Field(
        None,
        description="弹性模量 MPa",
    )
    i_mm4: Optional[float] = Field(
        None,
        description="截面惯性矩 mm^4",
    )
    l_mm: Optional[float] = Field(
        None,
        description="计算长度 mm",
    )
    load_kn: Optional[float] = Field(
        None,
        description="轴向工作载荷 kN",
    )
    mu: float = Field(
        1.0,
        description="欧拉稳定长度系数",
    )


@router.post("/column-strength")
def column_strength(req: ColumnStrengthReq):
    try:
        # ----------------------------------------------------
        # 1. 材料
        # ----------------------------------------------------
        if req.material not in MATERIALS:
            raise ValueError(
                f"材料 {req.material} 暂无已核实参数，当前可用："
                + "、".join(MATERIALS.keys())
            )

        mat = MATERIALS[req.material]

        sigma_s = mat.get("sigma_s")
        if sigma_s is None:
            raise ValueError(
                f"{req.material} 屈服强度未核实，不能执行强度计算"
            )

        sigma_allow = allowable_stress(
            sigma_s,
            req.material_safety_factor,
        )

        # ----------------------------------------------------
        # 2. 缸筒壁厚
        # ----------------------------------------------------
        delta_mm, regime = wall_thickness(
            req.d_mm,
            req.p_mpa,
            sigma_allow,
        )

        # ----------------------------------------------------
        # 3. 可选：应力校核
        # ----------------------------------------------------
        stress_result = None

        if req.sigma_max_mpa is not None:
            stress_sf, stress_ok = check_stress(
                req.sigma_max_mpa,
                sigma_s,
            )

            stress_result = {
                "sigma_max_mpa": req.sigma_max_mpa,
                "safety_factor": stress_sf,
                "ok": stress_ok,
            }

        # ----------------------------------------------------
        # 4. 可选：欧拉稳定校核
        # ----------------------------------------------------
        buckling_values = [
            req.e_mpa,
            req.i_mm4,
            req.l_mm,
            req.load_kn,
        ]

        any_buckling = any(v is not None for v in buckling_values)
        all_buckling = all(v is not None for v in buckling_values)

        if any_buckling and not all_buckling:
            raise ValueError(
                "稳定性校核参数必须完整提供："
                "e_mpa、i_mm4、l_mm、load_kn 四项缺一不可"
            )

        if req.mu <= 0:
            raise ValueError("长度系数 mu 必须大于0")

        buckling_result = None

        if all_buckling:
            pcr_kn, buckling_sf, buckling_ok = euler_buckling(
                req.e_mpa,
                req.i_mm4,
                req.l_mm,
                req.load_kn,
                req.mu,
            )

            buckling_result = {
                "critical_load_kn": pcr_kn,
                "safety_factor": buckling_sf,
                "ok": buckling_ok,
            }

        # ----------------------------------------------------
        # 5. 返回
        # ----------------------------------------------------
        data = {
            "material": {
                "name": req.material,
                "sigma_s_mpa": sigma_s,
                "sigma_b_mpa": mat.get("sigma_b"),
                "sigma_allow_mpa": sigma_allow,
                "material_safety_factor": req.material_safety_factor,
                "source": mat.get("source"),
            },
            "wall": {
                "thickness_mm": delta_mm,
                "regime": regime,
                "source": SOURCE_WALL,
            },
            "stress": stress_result,
            "buckling": buckling_result,
            "boundary_note": (
                "本结果用于公式复现、方案比较与参数设计辅助；"
                "材料性能、安全系数和边界条件应按实际设计资料复核，"
                "不直接作为产品制造依据。"
            ),
        }

        return {"code": 0, "data": data}

    except ValueError as e:
        return {"code": 1, "msg": str(e)}
