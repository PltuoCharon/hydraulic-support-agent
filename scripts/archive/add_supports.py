import re
import pandas as pd

# 格式：型号|架型|中心距m|厂商|来源
RAW_ADD = """
# ---- 郑煤机型谱补录（35型）----
ZY2200/11/22|掩护式|1.5|郑煤机|郑煤机型谱
ZY3400/10/17|掩护式|1.5|郑煤机|郑煤机型谱
ZY4000/08/20|掩护式|1.5|郑煤机|郑煤机型谱
ZY4000/11/25|掩护式|1.5|郑煤机|郑煤机型谱
ZY4000/15/32|掩护式|1.5|郑煤机|郑煤机型谱
ZY4000/16/35|掩护式|1.5|郑煤机|郑煤机型谱
ZY4000/17.5/38|掩护式|1.5|郑煤机|郑煤机型谱
ZY4800/09/21|掩护式|1.5|郑煤机|郑煤机型谱
ZY5200/11/26|掩护式|1.5|郑煤机|郑煤机型谱
ZY5200/14/32|掩护式|1.5|郑煤机|郑煤机型谱
ZY5200/17/35|掩护式|1.5|郑煤机|郑煤机型谱
ZY5200/18/38|掩护式|1.5|郑煤机|郑煤机型谱
ZY5200/19/43|掩护式|1.5|郑煤机|郑煤机型谱
ZY6800/20/42|掩护式|1.5|郑煤机|郑煤机型谱
ZY6800/21/45|掩护式|1.5|郑煤机|郑煤机型谱
ZY6800/24/50|掩护式|1.5|郑煤机|郑煤机型谱
ZY9000/11/22D|掩护式|1.75|郑煤机|郑煤机型谱
ZY9000/15/32|掩护式|1.75|郑煤机|郑煤机型谱
ZY9000/18/38|掩护式|1.75|郑煤机|郑煤机型谱
ZY9000/24/50|掩护式|1.75|郑煤机|郑煤机型谱
ZY9000/25.5/55|掩护式|1.75|郑煤机|郑煤机型谱
ZY10500/11/22D|掩护式|1.75|郑煤机|郑煤机型谱
ZY10000/17/35D|掩护式|1.75|郑煤机|郑煤机型谱
ZY12000/16/32D|掩护式|1.75|郑煤机|郑煤机型谱
ZY12000/25/50D|掩护式|1.75|郑煤机|郑煤机型谱
ZY12000/18/50D|掩护式|1.75|郑煤机|郑煤机型谱
ZY13000/28/60D|掩护式|1.75|郑煤机|郑煤机型谱
ZY15000/26/50D|掩护式|1.75|郑煤机|郑煤机型谱
ZY15000/29/60D|掩护式|1.75|郑煤机|郑煤机型谱
ZY15000/29/63D|掩护式|1.75|郑煤机|郑煤机型谱
ZY15000/33/67D|掩护式|1.75|郑煤机|郑煤机型谱
ZY18000/26.5/50D|掩护式|2.05|郑煤机|郑煤机型谱
ZY18000/28/55D|掩护式|2.05|郑煤机|郑煤机型谱
ZY18000/29/60D|掩护式|2.05|郑煤机|郑煤机型谱
ZY21000/34/72D|掩护式|2.05|郑煤机|郑煤机型谱
# ---- 其他厂商与文献（22型）----
ZY9000/20/40D|掩护式|1.5|平煤机|煤矿机械2023(千米埋深1.5m中心距设计)
ZY12000/32.5/72|掩护式|1.75|北京开采设计分院|国产大采高液压支架研究现状(矿业科学学报)
ZY5200/12/28|掩护式|1.5||宁夏发改委稳评报告(技术特征表)
ZYG5200/12/28|掩护式(过渡)|1.5||宁夏发改委稳评报告
ZYT5200/15/30D|端头支架|1.5||宁夏发改委稳评报告
ZY10800/28/63D|掩护式|1.75|国产|煤炭科学技术(大采高智能工作面跟机控制)
ZY18900/36/72D|掩护式||兰煤机|兰州煤机产品页(支护强度1.55-1.62,70t)
ZY13000/25/50D|掩护式|1.75|三一重装|浅谈ZY13000/25/50D研制(缸径420mm)
ZY8000/17.5/35|掩护式|1.75|三一重装|煤矿工作面设计(安全工程专业)
ZF7200/20/32|放顶煤|1.5|三一重装|综放工作面安装作业规程
ZF6400/16/30Q|放顶煤(大倾角)|1.5|河南能源重装|河南能源重装公司报道
ZFA10000/22/35D|放顶煤(低位)|1.5|河南能源重装|河南能源重装公司报道
ZF8600/20/38|放顶煤|1.5||上榆泉煤矿机电装备简介
ZY6600/19/39|掩护式|1.5||上榆泉煤矿机电装备简介
ZY2000/06/15|掩护式|1.5||煤矿支护手册
ZYL2200/06/17|掩护式|1.5||煤矿支护手册
ZYQ1700/09/22|掩护式(轻型)|1.5||煤矿支护手册
ZYQ1860/12/26|掩护式(轻型)|1.5||煤矿支护手册
ZY2000/10/26|掩护式|1.5||煤矿支护手册
ZYR200/16/32|掩护式|1.5||煤矿支护手册
ZY2500/13/32|掩护式|1.5||煤矿支护手册
ZY3200/13/32|掩护式|1.5||煤矿支护手册
"""

EXTRA_ADD = {
    "ZY5200/12/28": {"intensity": "0.57~0.68", "initial_force": 3879, "floor_pressure": "0.8~1.45"},
    "ZYG5200/12/28": {"intensity": "0.50~0.64", "initial_force": 3876},
    "ZY18900/36/72D": {"intensity": "1.55~1.62", "weight": 70},
    "ZY8000/17.5/35": {"initial_force": 7912},
    "ZF7200/20/32": {"initial_force": 6182, "weight": 19},
    "ZYR200/16/32": {"intensity": "0.47~0.53", "initial_force": 1595, "weight": 7.02},
    "ZY2500/13/32": {"intensity": "0.41~0.45", "initial_force": 1960, "weight": 8.3},
    "ZY3200/13/32": {"initial_force": 2354, "weight": 8.7},
}

def decode(model):
    m = re.search(r"[A-Z]+?(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", model)
    return int(float(m.group(1))), float(m.group(2)) / 10, float(m.group(3)) / 10

rows, bad = [], []
for line in RAW_ADD.strip().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = [x.strip() for x in line.split("|")]
    model, typ, cd, maker, src = parts
    try:
        r, h1, h2 = decode(model)
    except Exception:
        bad.append(model); continue
    row = {"model": model, "type": typ, "resistance": r,
           "height_min": h1, "height_max": h2,
           "center_dist": float(cd) if cd else None,
           "canopy_len": None, "intensity": None, "initial_force": None,
           "floor_pressure": None, "weight": None,
           "manufacturer": maker or None, "source": src}
    row.update(EXTRA_ADD.get(model, {}))
    rows.append(row)

new = pd.DataFrame(rows)
old = pd.read_excel("data/支架型号.xlsx")
merged = pd.concat([old, new], ignore_index=True)
merged = merged.drop_duplicates(subset="model", keep="first")  # 一型一行：重复保留先收录的
merged.to_excel("data/支架型号.xlsx", index=False)

print(f"新增解析 {len(new)} 型，解码失败 {bad}")
print(f"合并前 {len(old)} → 合并后 {len(merged)}（去重 {len(old)+len(new)-len(merged)} 条）")
print(merged.groupby("type").size())
