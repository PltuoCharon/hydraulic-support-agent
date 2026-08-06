"""CBR 匹配特征体系 + 野生文本归一化映射（论文表X-X代码化）"""

NUMERIC_FEATURES = {
    "coal_thickness": ("coal_thickness", None, "采高/m"),
    "dip_angle":      ("dip_angle",      None, "倾角/°"),
    "hardness_f":     ("hardness_f",     None, "煤硬度f"),
    "depth":          ("depth",          None, "埋深/m"),
}

ROOF_LEVELS = ["不稳定", "中等稳定", "稳定", "坚硬"]
PRESSURE_LEVELS = ["来压不明显", "来压明显", "来压剧烈", "强矿压"]
GAS_LEVELS = ["低瓦斯", "高瓦斯", "突出"]

ROOF_MAP = {
    "破碎": "不稳定", "复杂": "不稳定", "极软复杂": "不稳定",
    "浅埋薄基岩": "中等稳定", "浅埋": "中等稳定", "中等稳定": "中等稳定",
    "稳定": "稳定",
    "坚硬": "坚硬", "冲击": "坚硬", "深部": "坚硬",
}
PRESSURE_MAP = {
    "来压平缓": "来压不明显",
    "来压明显": "来压明显", "平均来压步距16m": "来压明显",
    "来压剧烈": "来压剧烈",
    "强矿压初次来压150m": "强矿压", "强冲击倾向": "强矿压",
    "重大冲击事故": "强矿压", "冲击停产": "强矿压",
}
GAS_MAP = {
    "低瓦斯": "低瓦斯", "低瓦斯煤层涌出量大": "低瓦斯",
    "高瓦斯(400m3/min)": "高瓦斯", "涌出量大": "高瓦斯",
    "高瓦斯突出矿区": "突出", "突出": "突出",
}

def normalize_categorical(raw, mapping):
    """野生文本 → 标准等级；未收录返回None(走中性分0.5)"""
    if raw is None:
        return None
    return mapping.get(str(raw).strip())
