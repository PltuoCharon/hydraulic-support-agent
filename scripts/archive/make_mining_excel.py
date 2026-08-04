import pandas as pd

columns = ["name", "category", "depth", "mining_height_min", "mining_height_max",
           "dip_angle", "hardness_f", "roof_category", "floor_pressure",
           "mine_pressure", "gas_level", "face_length",
           "support_model", "source"]

rows = [
    {"name": "补连塔12514", "category": "浅埋大采高", "depth": 277, "mining_height_min": 4.4, "mining_height_max": 8.8, "dip_angle": 2, "hardness_f": None, "roof_category": "浅埋薄基岩", "floor_pressure": None, "mine_pressure": "来压剧烈", "gas_level": "低瓦斯", "face_length": 327.7, "support_model": "ZY21000/36.5/80D", "source": "补连塔煤矿矿压规律分析方法应用研究"},
    {"name": "补连塔22304", "category": "浅埋大采高", "depth": None, "mining_height_min": 6.8, "mining_height_max": 6.8, "dip_angle": 2, "hardness_f": None, "roof_category": "直接顶粉砂岩砂质泥岩", "floor_pressure": None, "mine_pressure": None, "gas_level": "低瓦斯", "face_length": 301, "support_model": "ZY18000/32/70D", "source": "神东矿区世界一流矿井建设示范经验及实用技术"},
    {"name": "曹家滩122106", "category": "超大采高", "depth": 318, "mining_height_min": 8.0, "mining_height_max": 9.8, "dip_angle": None, "hardness_f": None, "roof_category": "多层厚硬岩层", "floor_pressure": None, "mine_pressure": "强矿压、初次来压约150m", "gas_level": None, "face_length": 300, "support_model": "ZYA29000/45/100D", "source": "中国煤炭科工集团10m超大采高工作面技术装备"},
    {"name": "塔山8102", "category": "坚硬顶板综放", "depth": 400, "mining_height_min": 3.5, "mining_height_max": 3.5, "dip_angle": 3, "hardness_f": 3, "roof_category": "坚硬(基本顶粉砂岩f=11.6)", "floor_pressure": None, "mine_pressure": "平均来压步距16m", "gas_level": "低瓦斯煤层涌出量大", "face_length": 231, "support_model": "ZF10000/25/38", "source": "塔山矿特厚煤层综放开采矿压显现规律初步研究"},
    {"name": "兴隆庄4301", "category": "综放", "depth": 265, "mining_height_min": 5.85, "mining_height_max": 9.4, "dip_angle": 5, "hardness_f": 2.3, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": 176, "support_model": None, "source": "兖州矿区综放面端头及两巷超前液压支架研制与应用"},
    {"name": "鲍店1316", "category": "综放", "depth": 357, "mining_height_min": 8.18, "mining_height_max": 8.74, "dip_angle": 6.5, "hardness_f": 3.5, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": 170, "support_model": None, "source": "兖州矿区综放面端头及两巷超前液压支架研制与应用"},
    {"name": "东滩矿", "category": "综放", "depth": None, "mining_height_min": 5.6, "mining_height_max": 6.5, "dip_angle": 5.5, "hardness_f": None, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": None, "support_model": None, "source": "我国综放开采40年及展望(煤炭学报2023)"},
    {"name": "晋城寺河", "category": "高瓦斯大采高", "depth": None, "mining_height_min": 5.2, "mining_height_max": 5.6, "dip_angle": None, "hardness_f": None, "roof_category": "顶板破碎", "floor_pressure": None, "mine_pressure": None, "gas_level": "高瓦斯(400m3/min)", "face_length": None, "support_model": "国产大采高支架(支高5.5m)", "source": "山西日报2004寺河煤矿报道;厚煤层开采技术文献"},
    {"name": "金鸡滩", "category": "大采高综放", "depth": None, "mining_height_min": 7.0, "mining_height_max": 7.0, "dip_angle": 1, "hardness_f": None, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": 300, "support_model": "ZY21000/38/70D", "source": "我国综放开采40年及展望(煤炭学报2023)"},
    {"name": "平朔安家岭", "category": "浅埋硬煤", "depth": 135, "mining_height_min": 7.0, "mining_height_max": 13.14, "dip_angle": None, "hardness_f": 2.5, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": 300, "support_model": "ZFY12000/23/40D", "source": "我国综放开采40年及展望;特大型矿井建设文献"},
    {"name": "潞安王庄", "category": "综放", "depth": None, "mining_height_min": None, "mining_height_max": None, "dip_angle": None, "hardness_f": None, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": "涌出量大", "face_length": 270, "support_model": "电液控制综放支架", "source": "我国综放开采40年的重大创新(2022)"},
    {"name": "潞安屯留", "category": "综放", "depth": None, "mining_height_min": None, "mining_height_max": None, "dip_angle": None, "hardness_f": None, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": None, "support_model": "ZF7000/19.5/38", "source": "创新煤炭安全高效开发技术支撑特大型矿井建设"},
    {"name": "神东黄玉川", "category": "综放缓斜", "depth": None, "mining_height_min": 3.5, "mining_height_max": 3.5, "dip_angle": 8.5, "hardness_f": None, "roof_category": None, "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": None, "support_model": "ZF21000/25/42D", "source": "我国综放开采40年及展望(煤炭学报2023)"},
    {"name": "淮北涡北", "category": "极软复杂", "depth": None, "mining_height_min": 9.0, "mining_height_max": 10.0, "dip_angle": None, "hardness_f": 0.2, "roof_category": "极软含夹矸", "floor_pressure": None, "mine_pressure": None, "gas_level": None, "face_length": None, "support_model": "ZF6800-19/38", "source": "我国综放开采40年及展望(煤炭学报2023)"},
    {"name": "新汶华丰1411", "category": "冲击地压深部", "depth": 960, "mining_height_min": 6.2, "mining_height_max": 6.2, "dip_angle": 32, "hardness_f": None, "roof_category": "直接顶中等冲击倾向", "floor_pressure": None, "mine_pressure": "强冲击倾向煤层", "gas_level": None, "face_length": None, "support_model": None, "source": "基于贝叶斯神经网络的冲击地压预测(中国矿业2022)"},
    {"name": "义马千秋21121", "category": "冲击地压", "depth": 800, "mining_height_min": 23.4, "mining_height_max": 23.4, "dip_angle": 11, "hardness_f": None, "roof_category": "特厚坚硬顶板", "floor_pressure": None, "mine_pressure": "重大冲击地压事故矿井", "gas_level": "低瓦斯", "face_length": 130, "support_model": None, "source": "安监总煤调[2011]171号通报;煤炭学报冲击地压文献"},
    {"name": "义马耿村13230", "category": "冲击地压", "depth": 800, "mining_height_min": 23.4, "mining_height_max": 23.4, "dip_angle": 11, "hardness_f": None, "roof_category": "坚硬顶板", "floor_pressure": None, "mine_pressure": "2015年冲击停产1年", "gas_level": None, "face_length": 196, "support_model": None, "source": "冲击地压煤矿深部开采煤岩动力灾害(煤炭学报)"},
    {"name": "淮南顾桥1313(3)", "category": "高瓦斯复杂", "depth": 612, "mining_height_min": 2.6, "mining_height_max": 5.8, "dip_angle": 5.5, "hardness_f": None, "roof_category": "复杂地质断层发育", "floor_pressure": None, "mine_pressure": "深部高地压", "gas_level": "高瓦斯突出矿区", "face_length": None, "support_model": None, "source": "顾桥煤矿大宽度工作面防火技术;淮南深部开采文献"},
]

df = pd.DataFrame(rows, columns=columns)
df.to_excel("data/矿区工况.xlsx", index=False)
print(f"已写入 {len(df)} 行，{df.shape[1]} 列")
print("类别分布：")
print(df["category"].value_counts())
