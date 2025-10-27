#!/bin/bash
# 慕班策思 - 启动脚本

echo "🚀 启动慕班策思系统..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.9"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python版本过低，需要 Python 3.9+"
    exit 1
fi

# 检查是否安装了依赖
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "📦 激活虚拟环境..."
source venv/bin/activate

echo "📦 安装/更新依赖..."
pip install -r requirements.txt -q

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env文件不存在，从.env.example复制..."
    cp .env.example .env
    echo "请编辑.env文件，填入你的API密钥"
    exit 1
fi

# 创建必要的目录
mkdir -p data/cache data/output data/approved_content

echo "✅ 准备完成！"
echo ""
echo "🌐 启动Web服务器..."
echo "   访问地址: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动应用
python main.py
