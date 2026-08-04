from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 加载 data/corpus/ 下全部 PDF
loader = DirectoryLoader("data/corpus", glob="*.pdf", loader_cls=PyPDFLoader)
docs = loader.load()
print(f"加载 {len(docs)} 页（来自 data/corpus/*.pdf）")

# 2. 切分：中文场景常用 500/50 起步
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块约500字符
    chunk_overlap=50,      # 块间重叠50字符，防止句子被拦腰截断
    separators=["\n\n", "\n", "。", "，", " ", ""]  # 按中文习惯优先从段落/句号处断开
)
chunks = splitter.split_documents(docs)
print(f"切成 {len(chunks)} 块")

# 3. 肉眼质检：看前 3 块
for i, c in enumerate(chunks[:3], 1):
    print(f"\n===== 块 {i}（{len(c.page_content)} 字符，来源：{c.metadata.get('source')}）=====")
    print(c.page_content)
