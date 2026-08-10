"""W18-D6 Agent 三问题演示：验证自主工具选择。
选型→run_matching；重算→recalc_params；规范→search_knowledge；查库→query_database。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.agent.agent import ask

QUESTIONS = [
    ("选型", "煤层厚度13米、倾角8度的综放工作面，推荐什么支架？"),
    ("重算", "立柱缸径从320mm换成360mm，工作阻力能提升多少？泵站压力31.5MPa不变。"),
    ("规范", "支护强度应该怎么确定？设计规范上怎么说的？"),
    ("查库", "补连塔矿区的煤层厚度和瓦斯等级是多少？"),
]

if __name__ == "__main__":
    for tag, q in QUESTIONS:
        print(f"\n{'='*20} [{tag}] {q}")
        r = ask(q)
        tools = [t for t, _ in r["steps"]]
        print("调用工具:", tools or "(无,直接回答)")
        print("回答:", r["answer"][:200])
