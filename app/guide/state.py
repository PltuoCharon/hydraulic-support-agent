"""引导式选型对话 State 定义。W19-D2。对应 docs/对话状态机设计.md 第 3 节。"""
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

# 必填与可选参数（追问策略见设计文档第 4 节）
REQUIRED = ["coal_thickness"]
OPTIONAL = ["dip_angle", "gas_level"]
PARAM_LABELS = {"coal_thickness": "煤层厚度(米)", "dip_angle": "煤层倾角(度)",
                "gas_level": "瓦斯等级(低瓦斯/高瓦斯/突出)"}

class GuideState(TypedDict, total=False):
    messages: Annotated[list, add_messages]   # LangGraph 消息历史(自动追加)
    params: dict          # 已收集参数 {"coal_thickness": 8.8, ...}
    missing: list[str]    # 缺失字段（节点代码确定性计算）
    stage: str            # collect / confirm / recommend / explain / recalc
    match_result: dict | None
    confirmed: bool

def calc_missing(params: dict) -> list[str]:
    """缺失字段 = 必填缺失 + 可选缺失。确定性计算，不靠模型自觉。"""
    return [k for k in REQUIRED + OPTIONAL if params.get(k) in (None, "")]
