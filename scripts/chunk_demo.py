"""文本切分 demo：纯 Python 实现，零依赖"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


class SimpleDocument:
    """简单文档对象，兼容 LangChain"""
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}


def load_text_files(directory):
    """加载目录下所有 txt 文件"""
    documents = []
    
    for root, dirs, files in os.walk(directory):
        for file in sorted(files):
            if file.endswith('.txt'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if content.strip():  # 非空文件
                        documents.append(SimpleDocument(
                            page_content=content,
                            metadata={'source': path}
                        ))
                        print(f"  ✓ 加载: {file} ({len(content)} 字符)")
                except Exception as e:
                    print(f"  ✗ 失败: {file} - {e}")
    
    return documents


def main():
    print("=" * 50)
    print("文本切分测试")
    print("=" * 50)
    
    # 1. 加载
    docs = load_text_files("data/corpus_text")
    print(f"\n总计: {len(docs)} 个文件")
    
    if len(docs) == 0:
        print("\n⚠️ 没有找到 txt 文件！")
        print("请先创建测试文本:")
        print("  mkdir -p data/corpus_text")
        print("  echo '内容...' > data/corpus_text/测试.txt")
        return
    
    # 2. 切分
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # 每块约500字符
        chunk_overlap=50,      # 重叠50字符
        separators=["\n\n", "\n", "。", "，", " ", ""]  # 中文优先
    )
    
    # 手动切分（兼容 SimpleDocument）
    chunks = []
    for doc in docs:
        texts = splitter.split_text(doc.page_content)
        for text in texts:
            chunks.append(SimpleDocument(
                page_content=text,
                metadata={**doc.metadata, 'chunk_size': len(text)}
            ))
    
    print(f"\n切成 {len(chunks)} 块")
    
    # 3. 肉眼质检
    print("\n" + "=" * 50)
    print("前 3 块质检")
    print("=" * 50)
    
    for i, c in enumerate(chunks[:3], 1):
        source = c.metadata.get('source', 'unknown')
        size = c.metadata.get('chunk_size', len(c.page_content))
        
        print(f"\n----- 块 {i} ({size} 字符, 来源: {os.path.basename(source)}) -----")
        preview = c.page_content[:300]
        print(preview)
        if len(c.page_content) > 300:
            print("...")
        print("-" * 40)
    
    # 4. 统计
    print("\n" + "=" * 50)
    print("统计信息")
    print("=" * 50)
    sizes = [c.metadata.get('chunk_size', 0) for c in chunks]
    print(f"总块数: {len(chunks)}")
    print(f"平均大小: {sum(sizes)//len(sizes) if sizes else 0} 字符")
    print(f"最小块: {min(sizes) if sizes else 0} 字符")
    print(f"最大块: {max(sizes) if sizes else 0} 字符")
    
    print("\n✅ 切分完成")


if __name__ == "__main__":
    main()
