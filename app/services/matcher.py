"""CBR 匹配服务薄壳(W28-D2 重构)。逻辑已迁 app/services/matching.py;
本文件仅保留 run_match 兼容签名。历史导入路径(NUM_W 等)请改用 matching 模块。"""
from app.services.matching import (  # noqa: F401  兼容旧导入, 过渡期保留
    NUM_FEATS, CASE_SQL, get_num_weights, build_diffs,
    load_area, load_cases, match_supports, match_by_params,
)

def run_match(area_id=None, coal_thickness=None, dip_angle=None, top_n=5) -> dict:
    """CBR 匹配主函数。异常: ValueError=参数互斥, LookupError=矿区不存在。
    返回: {"total": int, "items": [...]}"""
    if area_id and coal_thickness:
        raise ValueError("area_id 与手动工况只能二选一")
    if area_id:
        target = load_area(area_id)
        cases = load_cases(exclude_area_id=area_id)
    else:
        target = {"coal_thickness": coal_thickness, "dip_angle": dip_angle or 0,
                  "hardness_f": None, "depth": None, "roof_category": None,
                  "mine_pressure": None, "gas_level": None}
        cases = load_cases()
    return match_supports(target, cases, top_n)
