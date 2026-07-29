from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# 连接串：方言+驱动://用户:密码@主机:端口/库名?字符集
ENGINE_URL = "mysql+pymysql://hs_user:zyb123@127.0.0.1:3306/hydraulic_support?charset=utf8mb4"

engine = create_engine(ENGINE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Stent(Base):
    """支架表 stents 的 ORM 映射：类 ↔ 表，属性 ↔ 字段，对象 ↔ 一行"""
    __tablename__ = "stents"

    id = Column(Integer, primary_key=True)
    model = Column(String(50))
    type = Column(String(20))
    resistance = Column(Integer)
    height_min = Column(Float)
    height_max = Column(Float)
    center_dist = Column(Float)

    def __repr__(self):
        return f"<Stent {self.model} {self.resistance}kN>"


def find_by_height(mining_height):
    """按采高选型：支架高度范围能覆盖该采高的所有架型，按阻力降序"""
    session = Session()
    rows = session.query(Stent).filter(
        Stent.height_min <= mining_height,
        Stent.height_max >= mining_height
    ).order_by(Stent.resistance.desc()).all()
    session.close()
    return rows


def find_by_resistance(min_resistance):
    """按最低工作阻力筛选架型，按阻力降序"""
    session = Session()
    rows = session.query(Stent).filter(
        Stent.resistance >= min_resistance
    ).order_by(Stent.resistance.desc()).all()
    session.close()
    return rows


def find_by_height(mining_height):
    """按采高选型：支架高度范围能覆盖该采高的所有架型，按阻力降序"""
    session = Session()
    rows = session.query(Stent).filter(
        Stent.height_min <= mining_height,
        Stent.height_max >= mining_height
    ).order_by(Stent.resistance.desc()).all()
    session.close()
    return rows


def find_by_resistance(min_resistance):
    """按最低工作阻力筛选架型，按阻力降序"""
    session = Session()
    rows = session.query(Stent).filter(
        Stent.resistance >= min_resistance
    ).order_by(Stent.resistance.desc()).all()
    session.close()
    return rows
