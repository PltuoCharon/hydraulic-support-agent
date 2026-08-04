"""PDF OCR 文本提取：处理扫描件 PDF（内存优化版）"""

import os
import glob
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

PDF_DIR = "data/corpus"
OUTPUT_DIR = "data/corpus_text"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def ocr_pdf_chunked(pdf_path, dpi=200, batch_size=5):
    """分批 OCR，避免内存溢出"""
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")
    
    # 获取总页数
    from pdf2image import pdfinfo_from_path
    info = pdfinfo_from_path(pdf_path)
    total_pages = info["Pages"]
    
    print(f"\n📄 {base_name}: {total_pages} 页")
    
    all_texts = []
    
    # 分批处理
    for start in range(1, total_pages + 1, batch_size):
        end = min(start + batch_size - 1, total_pages)
        print(f"  处理 {start}-{end}/{total_pages} 页...")
        
        # 只转换当前批次
        images = convert_from_path(
            pdf_path,
            dpi=dpi,  # 降低分辨率节省内存
            first_page=start,
            last_page=end
        )
        
        # OCR 当前批次
        for i, image in enumerate(images, start):
            try:
                text = pytesseract.image_to_string(
                    image,
                    lang='chi_sim+eng',
                    config='--psm 6'
                )
                all_texts.append(f"--- 第{i}页 ---\n{text}")
            except Exception as e:
                print(f"    第{i}页失败: {e}")
            
            # 立即释放内存
            del image
        
        # 强制垃圾回收
        import gc
        gc.collect()
    
    # 保存
    full_text = "\n\n".join(all_texts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"  ✅ 完成: {output_path}")
    return output_path


def main():
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"发现 {len(pdf_files)} 个 PDF")
    
    for pdf_file in pdf_files:
        try:
            # 检查是否已有文本层
            import pdfplumber
            with pdfplumber.open(pdf_file) as pdf:
                has_text = any(p.extract_text() for p in pdf.pages[:2])
            
            if has_text:
                print(f"\n✓ {os.path.basename(pdf_file)} 有文本层，跳过")
                continue
            
            # OCR 处理
            ocr_pdf_chunked(pdf_file)
            
        except Exception as e:
            print(f"  ❌ 错误: {e}")


if __name__ == "__main__":
    main()
