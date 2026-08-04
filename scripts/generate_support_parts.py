"""为主力型号生成部件数据"""

import sys
sys.path.insert(0, '.')

from core.db import SessionLocal, SupportModel
from sqlalchemy import text


PARTS_TEMPLATES = {
    # 通用部件（所有型号都有）
    "通用": [
        ("立柱", "液压元件", "27SiMn", 4),
        ("千斤顶", "液压元件", "27SiMn", 8),
        ("顶梁", "结构件", "Q690", 1),
        ("掩护梁", "结构件", "Q690", 1),
        ("底座", "结构件", "Q690", 1),
        ("连杆", "结构件", "Q460", 2),
        ("推移千斤顶", "液压元件", "27SiMn", 2),
        ("平衡千斤顶", "液压元件", "27SiMn", 2),
    ],
    # 大采高特殊部件
    "大采高": [
        ("伸缩梁", "结构件", "Q690", 1),
        ("护帮板", "结构件", "Q460", 2),
        ("侧护板", "结构件", "Q460", 4),
    ],
    # 放顶煤特殊部件
    "放顶煤": [
        ("放煤机构", "执行机构", "Q690", 1),
        ("尾梁", "结构件", "Q690", 1),
        ("插板", "结构件", "Q460", 2),
    ],
    # 电液控制
    "电液": [
        ("控制器", "电控元件", "电子", 1),
        ("传感器", "检测元件", "电子", 4),
        ("电磁阀", "液压元件", "不锈钢", 8),
    ]
}


def get_model_type(model_name):
    """判断型号类型"""
    if '21000' in model_name or '15000' in model_name:
        return ["通用", "大采高", "电液"]
    elif 'ZF' in model_name:
        return ["通用", "放顶煤", "电液"]
    elif '12000' in model_name:
        return ["通用", "电液"]
    else:
        return ["通用"]


def generate_parts():
    """为主力型号生成部件"""
    
    with SessionLocal() as session:
        # 获取主力型号
        main_models = session.query(SupportModel).filter(
            SupportModel.model.in_([
                'ZY12000/28/58', 'ZY12000/28/62D',
                'ZY21000/36.5/80D', 'ZY21000/38/82D',
                'ZF15000/25/45', 'ZF18000/28/55',
                'ZZ10000/25/50', 'ZZ9600/22/45'
            ])
        ).all()
        
        print(f"主力型号: {len(main_models)} 个")
        
        generated = 0
        
        for model in main_models:
            model_types = get_model_type(model.model)
            parts_to_add = []
            
            # 收集所有部件
            for mt in model_types:
                if mt in PARTS_TEMPLATES:
                    parts_to_add.extend(PARTS_TEMPLATES[mt])
            
            # 去重
            seen = set()
            unique_parts = []
            for part in parts_to_add:
                key = part[0]  # 部件名
                if key not in seen:
                    seen.add(key)
                    unique_parts.append(part)
            
            # 插入数据库
            for part_name, part_type, material, quantity in unique_parts:
                session.execute(text("""
                    INSERT INTO support_parts 
                    (model_id, part_name, part_type, material, quantity)
                    VALUES (:model_id, :name, :type, :material, :qty)
                    ON DUPLICATE KEY UPDATE
                    material = VALUES(material),
                    quantity = VALUES(quantity)
                """), {
                    "model_id": model.id,
                    "name": part_name,
                    "type": part_type,
                    "material": material,
                    "qty": quantity
                })
                generated += 1
            
            print(f"  ✓ {model.model}: {len(unique_parts)} 个部件")
        
        session.commit()
        print(f"\n✅ 生成 {generated} 条部件记录")


if __name__ == "__main__":
    generate_parts()
