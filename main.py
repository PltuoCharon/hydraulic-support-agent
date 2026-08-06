from core.support import Cylinder, Support
from app.routers import match
app.include_router(match.router, prefix="/api/match", tags=["CBR匹配"])

# 组装一台 ZY12000/28/63D：4 根立柱，缸径 320mm
zy = Support(
    model="ZY12000/28/63D",
    cylinders=[Cylinder(320, 31.5)] * 4,
    center_dist=1.75,
    canopy_len=4.0
)

print(f"型号：{zy.model}")
print(f"单柱推力：{zy.cylinders[0].thrust():.1f} kN")
print(f"工作阻力：{zy.resistance():.0f} kN")
print(f"支护强度：{zy.intensity():.2f} MPa")

print("---- 修改缸径 320 → 360 ----")
for c in zy.cylinders:
    c.bore = 360

print(f"改后工作阻力：{zy.resistance():.0f} kN")
print(f"改后支护强度：{zy.intensity():.2f} MPa")

# ---- 交互式单柱推力计算（演示异常处理）----
try:
    bore = float(input("请输入缸径(mm)："))
    pressure = float(input("请输入压力(MPa)："))
    c = Cylinder(bore, pressure)
    print(f"单柱推力 {c.thrust():.1f} kN")
except ValueError:
    print("输入有误：请输入数字，例如 320 和 31.5")
