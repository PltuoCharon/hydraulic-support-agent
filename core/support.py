import math


class Cylinder:
    """液压支架立柱"""
    def __init__(self, bore_mm, pressure_mpa):
        self.bore = bore_mm            # 缸径 mm
        self.pressure = pressure_mpa   # 压力 MPa

    def thrust(self):
        """单柱推力，单位 kN。F = P × πD²/4"""
        area = math.pi * self.bore ** 2 / 4
        return self.pressure * area / 1000


class Support:
    """液压支架整架"""
    def __init__(self, model, cylinders, center_dist, canopy_len, eta=0.9):
        self.model = model              # 型号
        self.cylinders = cylinders      # Cylinder 对象列表
        self.center_dist = center_dist  # 中心距 m
        self.canopy_len = canopy_len    # 控顶长度 m
        self.eta = eta                  # 支撑效率

    def resistance(self):
        """工作阻力 kN = 各柱推力之和 × 支撑效率"""
        return sum(c.thrust() for c in self.cylinders) * self.eta

    def intensity(self):
        """支护强度 MPa = 工作阻力 / (中心距 × 控顶距) / 1000"""
        area = self.center_dist * self.canopy_len
        return self.resistance() / area / 1000


def normalize(arr):
    """最小-最大归一化到 [0,1]，用于多指标选型评价的预处理"""
    import numpy as np
    a = np.array(arr, dtype=float)
    return (a - a.min()) / (a.max() - a.min())
