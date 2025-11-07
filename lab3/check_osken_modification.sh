#!/bin/bash
# 检查 OS-Ken 源文件修改情况的脚本

OSKEN_FILE=".venv/lib/python3.13/site-packages/os_ken/topology/switches.py"

echo "=========================================="
echo "检查 OS-Ken 源文件修改情况"
echo "=========================================="
echo ""

if [ ! -f "$OSKEN_FILE" ]; then
    echo "❌ 错误：找不到文件 $OSKEN_FILE"
    echo "请确保虚拟环境已创建，并且 Python 版本为 3.13"
    exit 1
fi

echo "✅ 找到文件: $OSKEN_FILE"
echo ""

# 检查 PortData 类是否有 delay 和 timestamp 属性
echo "1. 检查 PortData 类..."
if grep -q "self.delay = 0" "$OSKEN_FILE" && grep -q "self.timestamp = None" "$OSKEN_FILE"; then
    echo "   ✅ PortData 类已包含 delay 和 timestamp 属性"
else
    echo "   ❌ PortData 类缺少 delay 或 timestamp 属性"
    echo "   需要添加："
    echo "   - self.timestamp = None"
    echo "   - self.delay = 0"
fi
echo ""

# 检查 lldp_packet_in_handler 是否有 recv_timestamp
echo "2. 检查 lldp_packet_in_handler 方法..."
if grep -q "recv_timestamp = time.time()" "$OSKEN_FILE"; then
    echo "   ✅ lldp_packet_in_handler 已包含 recv_timestamp"
else
    echo "   ❌ lldp_packet_in_handler 缺少 recv_timestamp"
    echo "   需要在方法开头添加：recv_timestamp = time.time()"
fi

if grep -q "port_data.delay = recv_timestamp - send_timestamp" "$OSKEN_FILE"; then
    echo "   ✅ lldp_packet_in_handler 已包含 delay 计算"
else
    echo "   ❌ lldp_packet_in_handler 缺少 delay 计算"
    echo "   需要添加计算 delay 的代码"
fi
echo ""

# 检查是否导入了 time 模块
echo "3. 检查 time 模块导入..."
if grep -q "^import time" "$OSKEN_FILE" || grep -q "^import time " "$OSKEN_FILE"; then
    echo "   ✅ 已导入 time 模块"
else
    echo "   ❌ 未导入 time 模块"
    echo "   需要在文件顶部添加：import time"
fi
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="
echo ""
echo "如果发现缺少修改，请参考 OSKEN_MODIFICATION.md 文件进行修改"

