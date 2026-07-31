import os
import pdfplumber
from pathlib import Path

CORPUS_DIR = "data/corpus"
OUTPUT_DIR = "data/corpus_text"

def extract_text(pdf_path):
    """提取 PDF 文本"""
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text)

def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    for pdf_file in Path(CORPUS_DIR).glob("**/*.pdf"):
        print(f"处理: {pdf_file}")
        
        # 生成输出路径
        rel_path = pdf_file.relative_to(CORPUS_DIR)
        out_path = Path(OUTPUT_DIR) / rel_path.with_suffix(".txt")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 提取文本
        try:
            text = extract_text(pdf_file)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"  ✓ 已保存: {out_path}")
        except Exception as e:
            print(f"  ✗ 失败: {e}")

if __name__ == "__main__":
    main()
