# Lab 3 快速开始指南 🚀

## 📋 准备工作清单

- [ ] 已进入 lab3 目录
- [ ] 已激活虚拟环境
- [ ] 已修改 OS-Ken 源文件（任务二需要）
- [ ] 已添加拓扑文件执行权限

## 🔧 环境设置

### 步骤 1：进入目录并设置环境

```bash
cd lab3
source setup.sh
```

### 步骤 2：添加执行权限

```bash
chmod +x topo.py
```

### 步骤 3：修改 OS-Ken 源文件（仅任务二需要）

**重要**：任务二需要修改 OS-Ken 源文件以支持时延测量。

查看详细说明：
```bash
cat OSKEN_MODIFICATION.md
```

编辑文件：
```bash
nano .venv/lib/python3.13/site-packages/os_ken/topology/switches.py
```

或使用 VSCode：
```bash
code .venv/lib/python3.13/site-packages/os_ken/topology/switches.py
```

---

## 📝 任务一：最少跳数路径

### 目标
- 理解 LLDP 拓扑发现
- 实现 ARP 环路检测
- 使用 NetworkX 计算最短路径

### 运行步骤

**终端 1（启动拓扑）：**
```bash
sudo ./topo.py
```

**终端 2（启动控制器）：**
```bash
uv run osken-manager least_hops.py --observe-links
```

**Mininet CLI（测试）：**
```bash
mininet> h2 ping -c 10 h9
```

### 预期结果

控制器输出：
```
path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> 1:s2:2 -> 1:s4:3 -> 1:s5:2 -> 3:s9:1 -> 10.0.0.9
```

Ping 成功（前几次可能失败，这是正常的"沉默主机"现象）。

---

## 🕐 任务二：最小时延路径

### 前置条件
⚠️ **必须先完成 OS-Ken 源文件修改！**

### 目标
- 测量链路时延（LLDP + Echo）
- 计算最小时延路径
- 验证 Ping RTT

### 运行步骤

**终端 1（启动拓扑）：**
```bash
sudo ./topo.py
```

**终端 2（启动控制器）：**
```bash
uv run osken-manager shortest_delay.py --observe-links
```

**Mininet CLI（测试）：**
```bash
mininet> h2 ping -c 10 h9
```

### 预期结果

控制器输出：
```
Link: 2 -> 3, delay: 32.00000ms
Link: 6 -> 7, delay: 20.00000ms
...
path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> ... -> s6 -> s7 -> s8 -> s9 -> 10.0.0.9
link delay dict: {'s2->s4': 80.0, 's4->s5': 110.0, ...}
path delay = 290.00000ms
path RTT = 580.00000ms
```

Ping RTT 应该接近计算的 path delay（约 270-290ms）。

---

## 🔧 任务三：链路故障容忍

### 目标
- 检测链路故障
- 自动切换路径
- 故障恢复后自动回切

### 运行步骤

使用任务二的相同设置（`shortest_delay.py`）。

**测试链路故障：**

**步骤 1：初始状态**
```bash
mininet> h2 ping h9
# 观察 RTT（约 270ms）和路径
```

**步骤 2：模拟链路故障**
```bash
mininet> link s6 s7 down
# 继续 ping，观察路径自动切换
# RTT 会增加到约 370ms
```

**步骤 3：恢复链路**
```bash
mininet> link s6 s7 up
# 观察路径自动恢复到最优路径
# RTT 恢复到约 270ms
```

### 预期结果

**故障前：**
```
path: ... -> s6 -> s7 -> s8 -> s9 -> ...
path delay = 270ms
```

**故障后：**
```
Port status changed on switch 6, port 2
Topology map cleared
All flow entries deleted
path: ... -> s5 -> s9 -> ...  (绕过 s6-s7)
path delay = 370ms
```

**恢复后：**
```
Port status changed on switch 6, port 2
Topology map cleared
path: ... -> s6 -> s7 -> s8 -> s9 -> ...  (恢复最优路径)
path delay = 270ms
```

---

## 🐛 常见问题

### 问题 1：时延出现负值

**现象：**
```
Link: 2 -> 3, delay: -5.23456ms
```

**原因：**
LLDP 和 Echo 测量是异步的，数据尚未就绪。

**解决：**
代码中已经使用 `max(delay, 0)` 处理，等待几秒后会自动修正。

---

### 问题 2："host not find/no path"

**现象：**
```
host not find/no path
host not find/no path
path: 10.0.0.2 -> 10.0.0.9  (第3次才成功)
```

**原因：**
沉默主机现象，主机未主动通信前控制器无法感知。

**解决：**
这是正常现象，前几次 ping 会自动触发主机发现。

---

### 问题 3：修改 OS-Ken 源文件后无效

**原因：**
Python 使用了缓存的 `.pyc` 文件。

**解决：**
```bash
# 删除缓存
find .venv -name "*.pyc" -delete
find .venv -name "__pycache__" -type d -exec rm -rf {} +

# 重启控制器
```

---

### 问题 4：链路故障后 ping 中断

**现象：**
```
Request timeout for icmp_seq 2
Request timeout for icmp_seq 3
64 bytes from 10.0.0.9: icmp_seq=4 ttl=64 time=370 ms
```

**原因：**
拓扑重新发现需要时间（约 2-3 秒）。

**解决：**
这是预期行为，说明故障检测正常工作。

---

## 📸 实验截图建议

### 任务一（3 张）
1. 控制器输出（路径信息）
2. Ping 成功截图
3. ARP 环路检测日志（如果有）

### 任务二（6 张）
1. 控制器输出（链路时延）
2. 控制器输出（link delay dict）
3. 控制器输出（path delay 和 path RTT）
4. Ping 输出（RTT 对比）
5. 代码截图（calculate_link_delay）
6. 代码截图（handle_echo_reply）

### 任务三（6 张）
1. 初始状态：控制器输出
2. 初始状态：Ping RTT
3. 故障状态：`link s6 s7 down` 命令
4. 故障状态：控制器输出（新路径）
5. 恢复状态：`link s6 s7 up` 命令
6. 恢复状态：控制器输出（恢复路径）

---

## 🧹 清理环境

**退出 Mininet：**
```bash
mininet> exit
```

**清理 Mininet 环境：**
```bash
sudo mn -c
```

**停止控制器：**
```bash
Ctrl + C
```

**退出虚拟环境：**
```bash
deactivate
```

---

## 📚 参考资料

- 详细实验指导：`README.md`
- OS-Ken 修改说明：`OSKEN_MODIFICATION.md`
- 代码文件：
  - `least_hops.py` - 任务一
  - `shortest_delay.py` - 任务二和三
  - `network_awareness.py` - 拓扑发现和时延测量

---

**祝实验顺利！** 🎉

