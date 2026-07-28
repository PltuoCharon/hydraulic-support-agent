from core.db import Session, Stent

session = Session()

# 查全部
print("== 全部支架 ==")
for s in session.query(Stent).all():
    print(s.model, s.type, s.resistance)

# 条件查询：等价于 WHERE resistance >= 10000 ORDER BY resistance DESC
print("== 高阻力架型 ==")
rows = session.query(Stent).filter(Stent.resistance >= 10000) \
                           .order_by(Stent.resistance.desc()).all()
for s in rows:
    print(s)

session.close()
