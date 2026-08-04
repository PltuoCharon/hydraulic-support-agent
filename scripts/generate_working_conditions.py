"""从 mining_areas 生成 working_conditions 数据"""

import sys
sys.path.insert(0, '.')

from core.db import SessionLocal, MiningArea, SupportModel
from sqlalchemy import text


def generate_conditions():
    """为每个矿区生成工况记录"""
    
    with SessionLocal() as session:
        # 获取所有矿区
        areas = session.query(MiningArea).all()
        print(f"共 {len(areas)} 个矿区")
        
        generated = 0
        
        for area in areas:
            # 查找匹配的支架型号
            support_model = None
            if area.support_model:
                support_model = session.query(SupportModel).filter(
                    SupportModel.model == area.support_model
                ).first()
            
            # 如果没有匹配，按类别推荐
            if not support_model:
                # 根据矿区类型推荐支架
                if '大采高' in area.category or '超大采高' in area.category:
                    support_model = session.query(SupportModel).filter(
                        SupportModel.model.like('%21000%')
                    ).first()
                elif '放顶煤' in area.category or '综放' in area.category:
                    support_model = session.query(SupportModel).filter(
                        SupportModel.model.like('%ZF%')
                    ).first()
                elif '冲击' in area.category:
                    support_model = session.query(SupportModel).filter(
                        SupportModel.working_resistance >= 15000
                    ).order_by(SupportModel.working_resistance.desc()).first()
                else:
                    support_model = session.query(SupportModel).filter(
                        SupportModel.model.like('%12000%')
                    ).first()
            
            support_model_id = support_model.id if support_model else None
            
            # 生成工作面名称
            working_face = f"{area.name}工作面"
            
            # 使用矿区数据填充工况
            session.execute(text("""
                INSERT INTO working_conditions 
                (area_id, support_model_id, working_face_name, coal_thickness, 
                 roof_condition, floor_condition, dip_angle, gas_level, 
                 mining_height, daily_output)
                VALUES 
                (:area_id, :support_model_id, :working_face, :coal_thickness,
                 :roof, :floor, :dip_angle, :gas_level, :mining_height, :output)
                ON DUPLICATE KEY UPDATE
                support_model_id = VALUES(support_model_id),
                coal_thickness = VALUES(coal_thickness)
            """), {
                "area_id": area.id,
                "support_model_id": support_model_id,
                "working_face": working_face,
                "coal_thickness": area.coal_thickness or area.mining_height_max,
                "roof": area.roof_category or "中等稳定",
                "floor": "坚硬",
                "dip_angle": area.dip_angle or 5.0,
                "gas_level": area.gas_level or "低瓦斯",
                "mining_height": area.mining_height_max or 4.0,
                "output": 8000
            })
            
            generated += 1
            print(f"  ✓ {area.name}: {support_model.model if support_model else '无匹配'}")
        
        session.commit()
        print(f"\n✅ 生成 {generated} 条工况记录")


if __name__ == "__main__":
    generate_conditions()
