"""智能体 10 条用例回归。W24 验收闸门3。达标线：通过≥8 且无编造数字。"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
results = []

def chat(msg, sid=None):
    r = client.post("/api/chat/", json={"message": msg, "session_id": sid})
    if r.status_code != 200:
        return {"http": r.status_code}
    d = r.json()
    return d.get("data", {})

def run_case(name, fn):
    try:
        ok, detail = fn()
        results.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    except Exception as e:
        results.append((name, False, f"异常 {e}"))
        print(f"[FAIL] {name}: 异常 {e}")

# 1 正常收集
def c1():
    d = chat("煤层厚度8.8米")
    return d.get("params", {}).get("coal_thickness") == 8.8, f"stage={d.get('stage')} params={d.get('params')}"
# 2 缺参追问
def c2():
    d = chat("推荐一个支架")
    return d.get("stage") == "collect" and len(d.get("missing", [])) > 0, f"missing={d.get('missing')}"
# 3 边界采高(最小)
def c3():
    d = chat("煤层厚度1米，倾角5度")
    return d.get("params", {}).get("coal_thickness") == 1, f"params={d.get('params')}"
# 4 瓦斯等级
def c4():
    d = chat("煤层厚度5米，倾角10度，高瓦斯")
    return d.get("params", {}).get("gas_level") == "高瓦斯", f"params={d.get('params')}"
# 5 大倾角
def c5():
    d = chat("煤层厚度4米，倾角40度")
    return d.get("params", {}).get("dip_angle") == 40, f"params={d.get('params')}"
# 6 连续追问(不500)
def c6():
    d1 = chat("推荐一个支架")
    d2 = chat("推荐一个支架", d1.get("session_id"))
    return d2.get("stage") in ("collect", "confirm_pending", "explained"), f"stage2={d2.get('stage')}"
# 7 为什么追问(出处+相似度)
def c7():
    d1 = chat("煤层厚度8.8米，倾角2度，低瓦斯")
    sid = d1.get("session_id")
    chat("对", sid)
    d3 = chat("为什么推荐它", sid)
    ok = d3.get("stage") == "explained" and "案例库" in d3.get("reply", "") and "相似度" in d3.get("reply", "")
    return ok, d3.get("stage")
# 8 乱码输入
def c8():
    d = chat("xyz123!!!")
    return d.get("stage") in ("collect", "confirm_pending", "explained"), f"stage={d.get('stage')}"
# 9 空输入
def c9():
    d = chat("")
    return d.get("stage") in ("collect", "confirm_pending", "explained"), f"stage={d.get('stage')}"
# 10 超长输入
def c10():
    d = chat("煤层" * 300)
    return d.get("stage") in ("collect", "confirm_pending", "explained"), f"stage={d.get('stage')}"

run_case("1 正常收集", c1)
run_case("2 缺参追问", c2)
run_case("3 边界采高", c3)
run_case("4 瓦斯等级", c4)
run_case("5 大倾角", c5)
run_case("6 连续追问", c6)
run_case("7 为什么追问", c7)
run_case("8 乱码输入", c8)
run_case("9 空输入", c9)
run_case("10 超长输入", c10)

passed = sum(1 for _, ok, _ in results if ok)
print(f"\n=== 汇总: {passed}/10 通过 （达标线 ≥8）===")
sys.exit(0 if passed >= 8 else 1)
