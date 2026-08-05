import csv, re, pymysql

def key(model):
    m = model.replace(" ", "").upper()
    mm = re.match(r'^([A-Z]+)(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)([A-Z]*)$', m)
    if not mm:
        return m
    pre, a, b, c, suf = mm.groups()
    def num(x):
        f = float(x)
        return str(int(f)) if f == int(f) else str(f)
    return f"{pre}{num(a)}/{num(b)}/{num(c)}{suf}"

conn = pymysql.connect(host="localhost", user="hs_user", password="zyb123",
                       database="hydraulic_support", charset="utf8mb4")
cur = conn.cursor()

# 先建索引：库里所有型号 -> 真实写法
cur.execute("SELECT model FROM support_models")
db_models = {key(r[0]): r[0] for r in cur.fetchall()}

ok, miss = 0, []
with open("data/fill_params.csv", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        real = db_models.get(key(row["model"]))
        if not real:
            miss.append(row["model"]); continue
        cur.execute(
            "UPDATE support_models SET intensity=%s, weight=%s, "
            "source=CONCAT(COALESCE(source,''),' | ',%s) WHERE model=%s",
            (row["intensity"] or None, row["weight"] or None,
             row["source"], real))
        ok += cur.rowcount

conn.commit(); conn.close()
print(f"成功回写 {ok} 条；未匹配 {len(miss)} 条: {miss}")
