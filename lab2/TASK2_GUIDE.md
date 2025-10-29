# Lab 2 任务二和任务三测试指南 🔁

## 🎯 任务概览

- **任务二之一**：禁用端口解决环路广播 (`loop_breaker_switch.py`)
- **任务二之二**：转发历史信息解决环路广播 (`loop_detecting_switch.py`)

---

## 🔁 任务二之一：禁用端口解决环路广播

### 📋 步骤 1：观察环路问题

#### 1.1 启动环境

**终端 1（控制器）：**
```bash
cd ~/桌面/lab/lab2
source .venv/bin/activate
osken-manager self_learning_switch.py
```

**终端 2（网络拓扑）：**
```bash
cd ~/桌面/lab/lab2
sudo ./topo_2.py
```

#### 1.2 观察环路现象

**在 Mininet CLI 中：**
```bash
# 尝试 ping（会失败或延迟极高）
mininet> h4 ping -c 5 h2
```

**预期现象**：
- ❌ ping 失败或延迟极高（>1000ms）
- ❌ 可能完全无响应

#### 1.3 查看流表（可选）

```bash
mininet> dpctl dump-flows
```

**观察**：
- `n_packets` 数量异常巨大（数十万甚至数百万）
- 这说明数据包在环路中不断循环

#### 1.4 Wireshark 抓包（可选）

```bash
mininet> h3 wireshark &
```

**观察**：
- 大量重复的 ARP Request 包
- Info 字段显示：`Who has 10.0.0.2? Tell 10.0.0.4`（不断重复）

---

### 📋 步骤 2：找出 s1 的端口号

**在 Mininet CLI 中（或重新启动）：**
```bash
mininet> h4 ping -c 3 h2
```

**切换到控制器终端（终端 1），观察输出：**

寻找 `dpid=1` 的日志，记录不同的 `in_port` 值。

**示例输出**：
```
Packet matched: dpid=1, src=..., in_port=2, dst=..., out_port=...
Packet matched: dpid=1, src=..., in_port=3, dst=..., out_port=...
Packet matched: dpid=1, src=..., in_port=4, dst=..., out_port=...
```

**记录端口号**：

根据 topo_2.py 的链路配置：
- s1-s2 链路
- s1-s3 链路
- s1-s4 链路
- s1-h1 链路

通过观察控制器输出，判断：
- s1 连接 s3 的端口：`___` （记录这个值）
- s1 连接 s4 的端口：`___` （记录这个值）

**提示**：可能需要多次 ping 才能看到所有端口的流量。

---

### 📋 步骤 3：清理环境

```bash
# 在 Mininet CLI 中
mininet> exit

# 在终端 2 中
$ sudo mn -c

# 在终端 1 中按 Ctrl+C 停止控制器
```

---

### 📋 步骤 4：修改 loop_breaker_switch.py

**编辑 `loop_breaker_switch.py` 文件：**

找到第 79 行：
```python
target_port = 2  # 请根据实际情况修改这个值
```

**修改为步骤 2 中找到的端口号**，例如：
- 如果 s1 连接 s3 的端口是 2，就填 `2`
- 如果 s1 连接 s4 的端口是 3，就填 `3`

---

### 📋 步骤 5：测试禁用端口方案

#### 5.1 禁用 s1 连接 s3 的端口

**假设 s1 连接 s3 的端口是 2**

编辑 `loop_breaker_switch.py` 第 79 行：
```python
target_port = 2
```

**启动环境：**

**终端 1：**
```bash
osken-manager loop_breaker_switch.py
```

**终端 2：**
```bash
sudo ./topo_2.py
```

**测试连通性：**
```bash
mininet> h4 ping -c 10 h2
```

**预期结果**：
- ✅ ping 成功！0% packet loss
- ✅ 延迟正常（100-200ms 左右）

**观察控制器输出：**
```
Port 2 on switch 1 has been disabled to break the loop
Packet matched: dpid=..., src=..., ...
```

**记录通信路径**：根据控制器输出的五元组，记录 h4 → h2 的路径。

---

#### 5.2 禁用 s1 连接 s4 的端口

**退出并清理：**
```bash
mininet> exit
$ sudo mn -c
# Ctrl+C 停止控制器
```

**假设 s1 连接 s4 的端口是 3**

编辑 `loop_breaker_switch.py` 第 79 行：
```python
target_port = 3
```

**重新启动环境并测试：**
```bash
# 终端 1
osken-manager loop_breaker_switch.py

# 终端 2
sudo ./topo_2.py

# Mininet CLI
mininet> h4 ping -c 10 h2
```

**预期结果**：
- ✅ ping 成功！
- ✅ 通信路径与禁用端口 2 时不同

**记录通信路径**：根据控制器输出，记录新的通信路径。

---

### 📋 步骤 6：对比分析

**对比两种情况的通信路径差异：**

#### 禁用 s1-s3 链路（端口 2）：
通信路径可能是：
```
h4 → s4 → s1 → s2 → h2
```
或
```
h4 → s4 → s2 → h2
```

#### 禁用 s1-s4 链路（端口 3）：
通信路径可能是：
```
h4 → s4 → s3 → s1 → s2 → h2
```

**分析**：不同端口禁用会改变数据包的转发路径，但都能消除环路。

---

### ✅ 任务二之一完成标志

- [ ] 能够观察到环路问题（ping 失败或延迟极高）
- [ ] 找出 s1 连接 s3 和 s4 的端口号
- [ ] 禁用端口后 ping 成功
- [ ] 对比不同端口禁用的通信路径差异
- [ ] 控制器日志显示 "Port X on switch 1 has been disabled"

---

## 🔍 任务二之二：转发历史信息解决环路广播

### 📋 步骤 1：测试环路检测方案

**清理环境：**
```bash
mininet> exit
$ sudo mn -c
# Ctrl+C 停止之前的控制器
```

**启动环境：**

**终端 1：**
```bash
cd ~/桌面/lab/lab2
source .venv/bin/activate
osken-manager loop_detecting_switch.py
```

**终端 2：**
```bash
sudo ./topo_2.py
```

---

### 📋 步骤 2：测试连通性

**在 Mininet CLI 中：**
```bash
mininet> h4 ping -c 10 h2
```

**预期结果**：
- ✅ ping 成功！0% packet loss
- ✅ 延迟正常

---

### 📋 步骤 3：观察控制器日志

**切换到终端 1（控制器），查看输出：**

**预期看到的日志类型：**

1. **记录 ARP Request：**
```
Recording ARP request: dpid=1, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=3
Recording ARP request: dpid=4, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=1
Recording ARP request: dpid=3, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=1
```

2. **检测到环路：**
```
Loop detected! Dropping ARP request: dpid=1, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=2 (previous port=3)
```

3. **正常的数据包匹配：**
```
Packet matched: dpid=..., src=..., in_port=..., dst=..., out_port=...
```

---

### 📋 步骤 4：分析环路检测逻辑

#### 环路检测机制

**数据结构**：
```python
self.sw = {}  # (dpid, src_mac, dst_ip) -> in_port
```

**检测逻辑**：
1. **第一次收到 ARP Request**：
   - 记录 `(dpid, src_mac, dst_ip) -> in_port`
   
2. **再次收到相同的 ARP Request**：
   - 检查 `(dpid, src_mac, dst_ip)` 是否已存在
   - 如果存在但 `in_port` 不同 → **检测到环路** → 丢弃包

#### 举例说明

**场景**：h4 (MAC: `AA:AA:AA:AA:AA:AA`) ping h2 (IP: `10.0.0.2`)

**步骤 1**：h4 发出 ARP Request 广播
```
ARP Request: Who has 10.0.0.2? Tell 10.0.0.4
```

**步骤 2**：广播传播
```
h4 → s4 → s1 (从端口 3 收到)
         ↓ 记录：(1, AA:AA:AA:AA:AA:AA, 10.0.0.2) -> 3
         ↓ 转发到 s2（正常）
         ↓ 转发到 s3（进入环路）
         
s3 → s4 → s1 (从端口 2 收到，环路返回！)
         ↓ 检查：(1, AA:AA:AA:AA:AA:AA, 10.0.0.2) 已存在
         ↓ 发现：之前是端口 3，现在是端口 2 (不同！)
         ↓ 判定：环路！
         ✅ 丢弃包，不再转发
```

**步骤 3**：正常通信继续
```
h2 收到 ARP Request → 回复 ARP Reply → h4 学习到 MAC → 开始 ping
```

---

### 📋 步骤 5：Wireshark 验证（可选）

```bash
mininet> h3 wireshark &
```

**过滤 ARP：**
```
arp
```

**观察**：
- ✅ 只有少量 ARP 包（正常的广播）
- ✅ 不再有大量重复的 ARP Request

**过滤 ICMP：**
```
icmp
```

**观察**：
- ✅ h3 不收到 h4 和 h2 之间的 ping 包（自学习成功）

---

### ✅ 任务二之二完成标志

- [ ] ping 成功（h4 和 h2 能正常通信）
- [ ] 控制器日志显示 "Recording ARP request"
- [ ] 控制器日志显示 "Loop detected! Dropping ARP request"
- [ ] 能够解释环路检测逻辑
- [ ] 能够举例说明检测过程

---

## 📊 实验报告记录表格

### 任务二之一：禁用端口

| 项目 | 记录内容 |
|-----|---------|
| s1 连接 s3 的端口号 | `___` |
| s1 连接 s4 的端口号 | `___` |
| 禁用端口 2 后的通信路径 | h4 → ... → h2 |
| 禁用端口 3 后的通信路径 | h4 → ... → h2 |
| 路径差异分析 | ... |

### 任务二之二：环路检测

| 项目 | 记录内容 |
|-----|---------|
| 首次记录的 ARP Request | dpid=___, in_port=___ |
| 检测到环路的端口 | dpid=___, in_port=___ (previous port=___) |
| 环路检测机制说明 | ... |
| 举例说明 | ... |

---

## 💡 常见问题

### Q1: 环路问题时 ping 卡住怎么办？

按 `Ctrl+C` 中断 ping，然后退出 Mininet：
```bash
mininet> exit
$ sudo mn -c
```

### Q2: 找不到 s1 的端口号？

多次尝试 ping，或者使用：
```bash
mininet> h1 ping -c 3 h2
mininet> h3 ping -c 3 h4
```

观察不同主机对之间的通信，从控制器输出中找出所有端口。

### Q3: loop_detecting_switch.py 没有显示环路检测日志？

确保：
1. 使用的是 `topo_2.py`（有环路）
2. 第一次 ping 时才会有 ARP Request
3. 可以重启网络再次测试

### Q4: 两种方法有什么区别？

| 方法 | 优点 | 缺点 |
|-----|-----|-----|
| 禁用端口 | 简单直接，永久消除环路 | 需要预先知道端口，破坏网络结构 |
| 转发历史检测 | 通用，不破坏网络结构 | 只针对 ARP Request，复杂度较高 |

---

## 🎉 完成！

完成以上步骤后，你就成功完成了 Lab 2 的所有任务！

记得：
- ✅ 截图保存关键步骤
- ✅ 记录控制器输出
- ✅ 填写实验报告表格
- ✅ 分析通信路径差异

祝你实验顺利！🚀

