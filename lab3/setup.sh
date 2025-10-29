#!/bin/bash

echo "=========================================="
echo "  Lab 3: 链路选择与故障恢复实验"
echo "  环境设置脚本"
echo "=========================================="
echo ""

# 同步依赖
echo "📦 正在同步项目依赖..."
uv sync

if [ $? -ne 0 ]; then
    echo "❌ 依赖同步失败，请检查错误信息"
    exit 1
fi

echo "✅ 依赖同步完成"
echo ""

# 激活虚拟环境
echo "🐍 正在激活 Python 虚拟环境..."
source .venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✅ 虚拟环境已激活"
    echo ""
    echo "=========================================="
    echo "  环境设置完成！"
    echo "=========================================="
    echo ""
    echo "📝 接下来的步骤："
    echo ""
    echo "1️⃣  添加执行权限："
    echo "    chmod +x topo.py"
    echo ""
    echo "2️⃣  修改 OS-Ken 源文件（任务二需要）："
    echo "    编辑: .venv/lib/python3.13/site-packages/os_ken/topology/switches.py"
    echo "    参考: lab3/README.md 中的详细说明"
    echo ""
    echo "3️⃣  运行任务一："
    echo "    终端 1: sudo ./topo.py"
    echo "    终端 2: uv run osken-manager least_hops.py --observe-links"
    echo ""
    echo "4️⃣  运行任务二："
    echo "    终端 1: sudo ./topo.py"
    echo "    终端 2: uv run osken-manager shortest_delay.py --observe-links"
    echo ""
    echo "5️⃣  在 Mininet CLI 中测试："
    echo "    mininet> h2 ping h9"
    echo "    mininet> link s6 s7 down  # 任务三：模拟故障"
    echo "    mininet> link s6 s7 up    # 任务三：恢复链路"
    echo ""
    echo "📖 详细指南请查看: lab3/README.md"
    echo ""
    echo "💡 提示：退出虚拟环境请输入 'deactivate'"
    echo "=========================================="
else
    echo "❌ 虚拟环境激活失败"
    exit 1
fi

