import numpy as np

RI = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45}

def ahp_weights(matrix):
    A = np.array(matrix, dtype=float)
    n = A.shape[0]
    eigvals, eigvecs = np.linalg.eig(A)
    idx = np.argmax(eigvals.real)
    lam_max = eigvals[idx].real
    w = eigvecs[:, idx].real
    w = w / w.sum()
    CI = (lam_max - n) / (n - 1)
    CR = CI / RI[n] if RI[n] else 0
    return {"weights": w.round(4).tolist(), "lambda_max": round(lam_max, 4),
            "CI": round(CI, 4), "CR": round(CR, 4), "consistent": CR < 0.1}

JUDGE_MATRIX = [
    [1,   2,   5,   3,   4  ],
    [1/2, 1,   4,   2,   3  ],
    [1/5, 1/4, 1,   1/2, 1/2],
    [1/3, 1/2, 2,   1,   2  ],
    [1/4, 1/3, 2,   1/2, 1  ],
]
FEATURE_ORDER = ["采高", "工作阻力", "倾角", "顶板类别", "矿压等级"]

if __name__ == "__main__":
    r = ahp_weights(JUDGE_MATRIX)
    for name, w in zip(FEATURE_ORDER, r["weights"]):
        print(f"  {name}: {w}")
    print(f"λmax={r['lambda_max']}  CI={r['CI']}  CR={r['CR']}  一致性{'通过' if r['consistent'] else '不通过!'}")
