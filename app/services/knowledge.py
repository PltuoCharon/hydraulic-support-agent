"""RAG 检索服务：对 knowledge_chunks 做关键词重叠打分，返回 Top-K 块及来源。
轻量方案(无向量库)，语料为 MT/T 556 标准。W18-D4。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.db import get_conn

def _ngrams(text: str, n: int = 2) -> set:
    t = re.sub(r"\s+", "", text)
    return {t[i:i+n] for i in range(len(t) - n + 1)}

def search(query: str, top_k: int = 3) -> list[dict]:
    """2-gram 重叠率打分。返回 [{source, loc, score, content}]。"""
    q = _ngrams(query)
    if not q:
        return []
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT source, loc, content FROM knowledge_chunks")
        rows = cur.fetchall()
    finally:
        conn.close()
    scored = []
    for r in rows:
        c = _ngrams(r["content"])
        hit = len(q & c)
        if hit:
            scored.append({**r, "score": round(hit / len(q), 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

if __name__ == "__main__":
    for r in search("支护强度怎么确定"):
        print(r["score"], r["loc"], r["content"][:80].replace("\n", " "), "\n---")
