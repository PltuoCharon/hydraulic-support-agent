-- W18-D4 RAG 知识库切块表
CREATE TABLE IF NOT EXISTS knowledge_chunks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(100) NOT NULL COMMENT '来源文件',
  loc VARCHAR(50) COMMENT '位置(页码/条款号)',
  content TEXT NOT NULL COMMENT '切块文本',
  INDEX idx_src (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='RAG知识切块';
