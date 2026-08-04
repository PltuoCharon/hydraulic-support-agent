"""SQLAlchemy ORM 模型：映射 support_models / mining_areas 等核心表"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# 数据库配置
DB_PASSWORD = os.getenv("DB_PASSWORD", "zyb123")
ENGINE_URL = f"mysql+pymysql://hs_user:{DB_PASSWORD}@127.0.0.1:3306/hydraulic_support?charset=utf8mb4"

engine = create_engine(ENGINE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class SupportModel(Base):
    """支架型号表 ORM"""
    __tablename__ = "support_models"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(50), unique=True, nullable=False, comment="型号")
    type = Column(String(20), comment="类型（掩护式/支撑式/支撑掩护式/放顶煤）")
    working_resistance = Column(Integer, comment="工作阻力(kN)")
    height_min = Column(DECIMAL(5, 2), comment="最小采高(m)")
    height_max = Column(DECIMAL(5, 2), comment="最大采高(m)")
    center_dist = Column(DECIMAL(6, 2), comment="中心距(m)")
    canopy_len = Column(DECIMAL(5, 2), comment="顶梁长度(m)")
    intensity = Column(String(20), comment="支护强度等级")
    initial_force = Column(Integer, comment="初撑力(kN)")
    floor_pressure = Column(String(20), comment="底板压力/矿压显现")
    weight = Column(Float, comment="重量(t)")
    manufacturer = Column(String(30), comment="生产厂家")
    source = Column(String(100), comment="数据来源")
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<SupportModel({self.model}, {self.type}, {self.working_resistance}kN)>"
    
    @classmethod
    def find_by_height(cls, session, h_min: float, h_max: float):
        """按采高范围查询"""
        return session.query(cls).filter(
            cls.height_min <= h_min,
            cls.height_max >= h_max
        ).all()
    
    @classmethod
    def find_by_resistance(cls, session, min_res: int):
        """按最小工作阻力查询"""
        return session.query(cls).filter(
            cls.working_resistance >= min_res
        ).order_by(cls.working_resistance.desc()).all()
    
    @classmethod
    def find_by_type(cls, session, stent_type: str):
        """按架型查询"""
        return session.query(cls).filter(
            cls.type.like(f"%{stent_type}%")
        ).all()


class MiningArea(Base):
    """矿区台账表 ORM"""
    __tablename__ = "mining_areas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    area_name = Column(String(50), nullable=False, comment="矿区名称")
    name = Column(String(50), unique=True, comment="矿区别名/标识")
    category = Column(String(20), comment="类型分类")
    depth = Column(DECIMAL(6, 2), comment="埋深(m)")
    mining_height_min = Column(DECIMAL(5, 2), comment="最小采高(m)")
    mining_height_max = Column(DECIMAL(5, 2), comment="最大采高(m)")
    coal_thickness = Column(DECIMAL(5, 2), comment="煤层厚度(m)")
    dip_angle = Column(DECIMAL(4, 1), comment="煤层倾角(度)")
    hardness_f = Column(DECIMAL(5, 2), comment="煤质硬度")
    roof_category = Column(String(20), comment="顶板分类")
    floor_pressure = Column(String(20), comment="底板压力")
    mine_pressure = Column(String(50), comment="矿压显现程度")
    gas_level = Column(String(20), comment="瓦斯等级")
    face_length = Column(DECIMAL(5, 2), comment="工作面长度(m)")
    support_model = Column(String(50), comment="在用支架型号")
    source = Column(String(100), comment="数据来源")
    is_test = Column(Integer, default=0, comment="盲测集标记")
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<MiningArea({self.name}, {self.category})>"
    
    @classmethod
    def get_train_set(cls, session):
        """获取训练集（排除盲测集）"""
        return session.query(cls).filter(cls.is_test == 0).all()
    
    @classmethod
    def get_test_set(cls, session):
        """获取盲测集"""
        return session.query(cls).filter(cls.is_test == 1).all()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # 测试 ORM
    from sqlalchemy import text
    
    with SessionLocal() as session:
        # 测试 SupportModel
        print("=== SupportModel 测试 ===")
        count = session.query(SupportModel).count()
        print(f"支架型号总数: {count}")
        
        # 测试按采高查询
        results = SupportModel.find_by_height(session, 2.0, 4.0)
        print(f"采高 2.0-4.0m 的支架: {len(results)} 条")
        for r in results[:3]:
            print(f"  {r.model}: {r.height_min}~{r.height_max}m, {r.working_resistance}kN")
        
        # 测试 MiningArea
        print("\n=== MiningArea 测试 ===")
        train = MiningArea.get_train_set(session)
        test = MiningArea.get_test_set(session)
        print(f"训练集: {len(train)} 条")
        print(f"盲测集: {len(test)} 条")
        for t in test:
            print(f"  [盲测] {t.name}: {t.category}")
