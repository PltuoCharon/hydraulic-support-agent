from pydantic import BaseModel, Field
from typing import Optional

class RecommendReq(BaseModel):
    """选型推荐请求：字段约束即业务规则，非法输入在API入口就被422拦下"""
    seam_thickness: float = Field(gt=0.5, lt=10, description="采高/m")
    gas_level: str = Field(pattern="^(低瓦斯|高瓦斯|突出)$", description="瓦斯等级")
    dip_angle: float = Field(default=0, ge=0, le=45, description="煤层倾角/°")
    # gt/> lt/< ge/≥ le/≤：数值范围；pattern：正则枚举

class SupportOut(BaseModel):
    """支架信息响应模型：也用于约束接口返回结构"""
    model: str
    work_force: Optional[float] = None
    intensity: Optional[float] = None
    weight: Optional[float] = None
    data_status: str = "verified"
