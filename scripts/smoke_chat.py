"""chat 状态机冒烟: 追问→确认→推荐, 断言 tools 含 run_matching。"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000/api/chat/"


def post(msg, sid=None):
    body = {"message": msg}
    if sid:
        body["session_id"] = sid
    req = urllib.request.Request(BASE, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["data"]


d1 = post("煤层8.8米")
assert d1["missing"], f"首轮应缺参: {d1}"
d2 = post("倾角2度，低瓦斯", d1["session_id"])
assert d2["stage"] == "confirm_pending", f"二轮应待确认: {d2}"
d3 = post("对", d1["session_id"])
assert d3["stage"] == "explained" and "run_matching" in d3["tools"], f"三轮应推荐: {d3}"
print("smoke_chat OK:", d3["reply"][:50])
