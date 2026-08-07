"""熵权法（客观权重）：对案例库数值特征计算信息熵，熵越小判别力越强、权重越大。W16-D4。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import numpy as np
from app.services.normalize import MinMaxScaler

def entropy_weights(cases: list[dict], features: list[str]) -> dict[str, float]:
    n = len(cases)
    if n == 0:
        return {f: 1.0 / len(features) for f in features}
    X = np.zeros((n, len(features)))
    for j, f in enumerate(features):
        sc = MinMaxScaler([c.get(f) for c in cases])
        X[:, j] = [v if v is not None else 0.5
                   for v in (sc.transform(c.get(f)) for c in cases)]
    X = X + 1e-4
    P = X / X.sum(axis=0, keepdims=True)
    k = 1.0 / np.log(n)
    e = -k * (P * np.log(P)).sum(axis=0)
    d = 1.0 - e
    if d.sum() == 0:
        return {f: 1.0 / len(features) for f in features}
    w = d / d.sum()
    return {f: round(float(wi), 4) for f, wi in zip(features, w)}

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from app.db import get_conn
    from app.services.filter import effective_height
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""
        SELECT wc.coal_thickness, wc.mining_height, ma.dip_angle, ma.hardness_f, ma.depth
        FROM working_conditions wc JOIN mining_areas ma ON ma.id = wc.area_id
        WHERE ma.is_test = 0
    """)
    cases = cur.fetchall()
    for c in cases:
        c["_eff_h"] = effective_height(c)
    feats = ["_eff_h", "coal_thickness", "dip_angle", "hardness_f", "depth"]
    print("熵权结果:", entropy_weights(cases, feats))
