"""W30-D2 厂商接口守恒校验: known + unknown == total, 未知居首"""
import json
import urllib.request

d = json.load(urllib.request.urlopen("http://127.0.0.1:8000/api/supports/vendors"))["data"]
assert d["known"] + d["unknown"] == d["total"], "total 不守恒"
assert d["items"][0]["manufacturer"] == "未知", "未知未居首"
assert d["coverage"] == round(d["known"] / d["total"] * 100, 1), "coverage 口径错"
print(f"vendors OK: total={d['total']} known={d['known']} unknown={d['unknown']} coverage={d['coverage']}%")
