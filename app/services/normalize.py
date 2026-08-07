from app.core.numparse import parse_number

class MinMaxScaler:
    """min-max归一化: x'=(x-min)/(max-min)，范围取案例库自身"""
    def __init__(self, values: list):
        vals = [parse_number(v) for v in values]
        vals = [v for v in vals if v is not None]
        self.min, self.max = (min(vals), max(vals)) if vals else (0, 1)

    def transform(self, v):
        x = parse_number(v)
        if x is None:
            return None
        if self.max == self.min:
            return 0.5
        return min(1.0, max(0.0, (x - self.min) / (self.max - self.min)))

def categorical_score(case_val, target_val, levels, adjacent=0.5, mismatch=0.0):
    """完全一致1 / 相邻等级0.5 / 不符0 / 缺失中性0.5"""
    if not case_val or not target_val:
        return 0.5
    c, t = str(case_val).strip(), str(target_val).strip()
    if c == t:
        return 1.0
    try:
        if abs(levels.index(c) - levels.index(t)) == 1:
            return adjacent
    except ValueError:
        for lv in levels:
            if c.startswith(lv[:4]) or t.startswith(lv[:4]):
                return adjacent
    return mismatch
