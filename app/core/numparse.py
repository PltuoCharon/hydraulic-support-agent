import re

def parse_number(v, ndigits=4):
    """库里的数值字段统一转float:
    Decimal/int/float → float; '1.0~1.045'区间文本 → 中值; 无法解析 → None"""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("～", "~").replace("—", "-").strip()
    nums = re.findall(r"\d+\.?\d*", s)
    if not nums:
        try:
            from decimal import Decimal
            return float(Decimal(s))
        except Exception:
            return None
    vals = [float(n) for n in nums[:2]]
    return round(sum(vals) / len(vals), ndigits)
