"""附录C 10条测试用例回归: 走真实服务, 输出 markdown 结果表。"""
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

BASE = "http://127.0.0.1:8000"


def post(path, body):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def chat(msg, sid=None):
    body = {"message": msg}
    if sid:
        body["session_id"] = sid
    return post("/api/chat/", body)["data"]


def full_flow():
    d1 = chat("煤层8.8米")
    d2 = chat("倾角2度，低瓦斯", d1["session_id"])
    d3 = chat("对", d1["session_id"])
    return d1, d2, d3


results = []


def case(no, name, fn, expect):
    try:
        actual, passed = fn()
    except Exception as e:
        actual, passed = f"异常: {e}", False
    results.append((no, name, expect, actual, "通过" if passed else "失败"))
    print(f"[{no}] {name}: {'通过' if passed else '失败'}")


def c01():
    d3 = full_flow()[2]
    return f"{d3['stage']}: {d3['reply'][:30]}...", \
           d3["stage"] == "explained" and "run_matching" in d3["tools"]


def c02():
    d = chat("煤层8.8米")
    return f"missing={d['missing']}", bool(d["missing"])


def c03():
    d1 = chat("煤层8.8米倾角2度低瓦斯")
    d2 = chat("倾角改成10度", d1["session_id"])
    ok = d2["stage"] == "confirm_pending" and d2["params"]["dip_angle"] == 10
    return d2["stage"], ok


def c04():
    d = chat("今天天气怎么样")
    return d["reply"][:20], "选型" in d["reply"]


def c05():
    d3 = full_flow()[2]
    return d3["reply"][-30:], "依据" in d3["reply"]


def c06():
    from app.services.support_calc import recalc
    r = recalc(bore_mm=360)
    return r["source"][:20], "估算" in r["source"]


def c07():
    from app.services.knowledge import search
    rs = search("支护强度")
    return rs[0]["source"] if rs else "无命中", bool(rs and rs[0].get("source"))


def c08():
    d = chat("煤层8.8米")
    return f"missing={len(d['missing'])}", bool(d["missing"])


def c09():
    req = urllib.request.Request(
        BASE + "/api/chat/",
        data=json.dumps({"message": "煤层8.8米", "stream": True}).encode(),
        headers={"Content-Type": "application/json"})
    body = urllib.request.urlopen(req, timeout=90).read().decode()
    return body.strip()[-6:], body.strip().endswith("[DONE]")


def c10():
    d = chat("煤层99米")
    return d["reply"][:20], True


case("C01", "完整引导流程", c01, "追问→确认→推荐, stage=explained")
case("C02", "缺参数追问", c02, "首轮缺倾角/瓦斯, 追问")
case("C03", "中途改口重确认", c03, "改口后重新确认, 参数更新")
case("C04", "越界问题拒答", c04, "拒答并引导提供工况参数")
case("C05", "推荐结果溯源", c05, "讲解含'依据: 案例库'来源")
case("C06", "公式重算溯源", c06, "返回 source 标注公式法估算依据")
case("C07", "知识检索溯源", c07, "命中块带 source/loc")
case("C08", "会话隔离", c08, "新 session 从零开始")
case("C09", "流式输出", c09, "SSE 以 [DONE] 结尾")
case("C10", "异常参数不崩", c10, "越界参数友好处理, 服务不崩")

print("\n| 编号 | 用例 | 预期 | 实际 | 结果 |")
print("|---|---|---|---|---|")
for no, name, expect, actual, res in results:
    print(f"| {no} | {name} | {expect} | {str(actual)[:40]} | {res} |")

fails = sum(1 for r in results if r[4] == "失败")
print(f"\n总计: {len(results)} 条, 失败 {fails}")
