#!/bin/bash
cd ~/hs_agent
source venv/bin/activate

echo "=== 修复 M3 验收问题 ==="

# 1. 安装依赖
echo "1. 安装 unstructured..."
pip install unstructured -i https://mirrors.aliyun.com/pypi/simple/ 2>/dev/null || echo "跳过，使用简单加载器"

# 2. 创建测试文本（如果没有）
echo "2. 检查语料..."
if [ ! -d "data/corpus_text" ] || [ -z "$(ls data/corpus_text/)" ]; then
    mkdir -p data/corpus_text
    cat > data/corpus_text/液压支架概述.txt << 'INNEREOF'
液压支架是煤矿综采工作面的关键设备。它主要用于支撑顶板，保护采煤机和人员安全。

液压支架按结构可分为掩护式、支撑式和支撑掩护式三种基本类型。掩护式支架适用于破碎顶板条件，具有较好的掩护性能。

大采高液压支架是指最大采高超过5米的液压支架，主要用于厚煤层一次采全高开采。目前国内最大采高已达8.8米。

冲击地压液压支架需要具备高强度和抗冲击能力，通常配备有特殊的防冲装置和监测系统。

放顶煤液压支架用于特厚煤层的放顶煤开采工艺，具有特殊的放煤机构和控制系统。

液压支架的主要技术参数包括：工作阻力、初撑力、支护强度、采高范围、中心距等。这些参数直接影响支架的支护性能和使用范围。

选型设计应根据煤层地质条件、顶板条件、瓦斯情况等因素综合考虑，确保支架与工况匹配。
INNEREOF
    echo "  ✅ 创建测试文本"
fi

# 3. 运行 chunk_demo
echo "3. 运行文本切分..."
python scripts/chunk_demo.py

echo "=== 修复完成 ==="
