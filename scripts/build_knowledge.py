"""知识库构建：PDF → 按页切块(带条款感知) → knowledge_chunks 表。W18-D4。
目前语料: MT/T 556-1996 液压支架设计规范(文字版)。重复执行幂等(先清后插)。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pypdf import PdfReader
from app.db import get_conn

PDFS = ["corpus/MT_T_556-1996_液压支架设计规范.pdf"]

def chunk_pdf(path: str):
    """按页提取，页内按条款(数字.x 或 第x条)边界粗切，小块合并到≥200字。"""
    reader = PdfReader(path)
    source = os.path.basename(path)
    chunks, buf, buf_loc = [], "", ""
    for pno, page in enumerate(reader.pages, 1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        for para in re.split(r"\n(?=\s*(?:\d+\.\d+|\d+、|第\d+条))", text):
            para = re.sub(r"\s+", " ", para).strip()
            if not para:
                continue
            if buf and len(buf) + len(para) > 600:
                chunks.append((source, buf_loc, buf))
                buf, buf_loc = "", ""
            if not buf:
                buf_loc = f"p{pno}"
            buf += para + "\n"
    if buf:
        chunks.append((source, buf_loc, buf.strip()))
    return chunks

def main():
    all_chunks = []
    for p in PDFS:
        cs = chunk_pdf(p)
        print(f"{p}: {len(cs)} 块")
        all_chunks.extend(cs)
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM knowledge_chunks")   # 幂等重建
    cur.executemany(
        "INSERT INTO knowledge_chunks(source, loc, content) VALUES (%s,%s,%s)",
        all_chunks)
    conn.commit()
    cur.execute("SELECT COUNT(*) c FROM knowledge_chunks")
    print("入库:", cur.fetchone()["c"], "块")

if __name__ == "__main__":
    main()
