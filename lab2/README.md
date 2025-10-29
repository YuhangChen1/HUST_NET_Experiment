# Lab 2: SDN 自学习与环路检测实验 🌐

## 📚 实验概述

本实验基于 OpenFlow/OS-Ken 控制器与 Mininet 仿真环境构建软件定义网络（SDN），实现交换机自学习和环路广播防治。

### 🎯 实验任务

- ✅ **任务一**：实现交换机自学习（`self_learning_switch.py`）
- ✅ **任务二之一**：使用端口禁用防止环路广播（`loop_breaker_switch.py`）
- ✅ **任务二之二**：使用转发历史信息防止环路广播（`loop_detecting_switch.py`）

### 📖 实验收获

- 熟悉并掌握网络工具的基本使用
- 熟悉并理解 SDN 的工作机制
- 了解 SDN 下的自学习与一般网络下的差异
- 了解环路广播的形成原因，掌握环路广播防治方法

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 进入 lab2 目录
cd ~/桌面/lab/lab2

# 一键设置环境（推荐）
source setup.sh

# 或者手动执行
uv sync
source .venv/bin/activate
```

### 2. 添加执行权限

```bash
chmod +x topo_1.py topo_2.py
```

---

## 📝 任务一：自学习交换机

### 🎯 任务目标

实现 MAC 地址自学习，避免无脑洪泛所有端口。

### 🌐 网络拓扑（topo_1.py）

```
    h1 --- s1 --- s2 --- h2
            |      |
            s3    s4
            |      |
            h3    h4
```

- **4 个主机**：h1, h2, h3, h4
- **4 个交换机**：s1, s2, s3, s4
- **无环路**

### 🔧 实验步骤

#### 步骤 1：验证简单交换机的缺陷

**终端 1：启动控制器**
```bash
osken-manager simple_switch.py
```

**终端 2：启动网络拓扑**
```bash
sudo ./topo_1.py
```

**Mininet CLI 中：**
```bash
# 启动 Wireshark 抓包（h3 端口）
mininet> h3 wireshark &

# h4 ping h2
mininet> h4 ping -c 3 h2
```

**观察现象**：
- ❌ h3 会收到 h4 和 h2 之间的通信包（不应该收到）
- 原因：`simple_switch.py` 使用洪泛，向所有端口转发

**清理环境：**
```bash
mininet> exit
$ sudo mn -c
```

---

#### 步骤 2：测试自学习交换机

**终端 1：启动控制器**
```bash
osken-manager self_learning_switch.py
```

**终端 2：启动网络拓扑**
```bash
sudo ./topo_1.py
```

**Mininet CLI 中：**
```bash
# 启动 Wireshark 抓包（h3 端口）
mininet> h3 wireshark &

# h4 ping h2
mininet> h4 ping -c 10 h2
```
**注意&符号不能丢**

**观察现象**：
- ✅ h3 只收到 ARP 广播包，不再收到 h4 和 h2 之间的 ICMP 包
**tip：ICMP包不是ICMPv6包 那是linux自己发的**
- ✅ 控制器终端显示五元组信息：`(dpid, src_mac, in_port, dst_mac, out_port)`

**示例输出**：
```
Packet matched: dpid=1, src=00:00:00:00:00:04, in_port=3, dst=00:00:00:00:00:02, out_port=1
Packet matched: dpid=1, src=00:00:00:00:00:02, in_port=1, dst=00:00:00:00:00:04, out_port=3
```

---

#### 步骤 3：分析 MAC 地址和端口号

根据控制器输出，分析：

**问题 1**：h2 和 h4 的 MAC 地址是什么？
- **答案**：从输出可以看出
  - h4 的 MAC：`00:00:00:00:00:04`
  - h2 的 MAC：`00:00:00:00:00:02`

**问题 2**：h2 和 h4 连接到哪个交换机的哪个端口？
- **答案**：
  - h4 连接到交换机 s1 的端口 3
  - h2 连接到交换机 s1 的端口 1（或通过 s2）

---

#### 步骤 4：测试 hard_timeout 参数

**修改 `self_learning_switch.py` 第 82 行：**

```python
# 场景 1：hard_timeout=0（流表永久有效）
self.add_flow(dp, 1, match, actions, hard_timeout=0)

# 场景 2：hard_timeout=5（流表 5 秒后失效）
self.add_flow(dp, 1, match, actions, hard_timeout=5)
```

**测试场景 1（hard_timeout=0）：**
```bash
mininet> h4 ping -c 20 h2
```
- **观察**：只有前几个包会触发控制器（学习阶段），之后控制器不再输出
- **原因**：流表永久有效，交换机直接转发，不经过控制器

**测试场景 2（hard_timeout=5）：**
```bash
mininet> h4 ping -c 20 h2
```
- **观察**：每隔 5 秒，控制器会再次输出日志
- **原因**：流表 5 秒后失效，需要重新学习

---


### ✅ 任务一验证清单

- [ ] h3 不再收到 h4 和 h2 之间的 ICMP 包
- [ ] 控制器输出五元组信息
- [ ] 能够分析出 MAC 地址和端口号
- [ ] 理解 hard_timeout 参数的作用

---

## 🔁 任务二之一：禁用端口解决环路广播

### 🎯 任务目标

通过禁用交换机端口打破网络环路。

### 📖 实验目的

**本任务的核心目的**：
1. **观察环路广播问题**：理解 ARP 广播在环路中无限循环的现象
2. **学习端口禁用方法**：掌握使用 OFPPortMod 消息禁用端口
3. **认识方法局限性**：体会在复杂拓扑中，单一端口禁用可能无法完全解决环路
4. **对比两种方案**：为任务二之二（转发历史检测）提供对比基础

⚠️ **重要说明**：
- 本任务中的 topo_2.py 拓扑设计了**多个相互嵌套的环路**
- 禁用 s1 的单个端口**可能无法完全解决环路问题**（这是故意设计的）
- 这正是为了展示**端口禁用方法的局限性**，引出任务二之二的通用解决方案

### 🌐 网络拓扑（topo_2.py）

```
    h1 --- s1 --- s2 --- h2
          /|\  
         / | \  
        s3-+-s4
        |     |
        h3    h4
```

**链路关系**：
- s1-s2, s1-s3, s1-s4（s1 连接其他三个交换机）
- s3-s4（额外的直连链路）

**环路结构**：
- 环路 1：s1 ↔ s3 ↔ s4 ↔ s1
- 环路 2：s1 ↔ s2 ↔ ... ↔ s4 ↔ s1（通过其他路径）

- **4 个主机**：h1, h2, h3, h4
- **4 个交换机**：s1, s2, s3, s4
- **存在多个嵌套环路**

### 🔧 实验步骤

#### 步骤 1：观察环路广播问题

**终端 1：启动控制器**
```bash
osken-manager self_learning_switch.py
```

**终端 2：启动网络拓扑**
```bash
sudo ./topo_2.py
```

**Mininet CLI 中：**
```bash
# 尝试 ping（会失败）
mininet> h4 ping -c 3 h2
# 会发现无法正常通信或延迟极高

# 查看流表（数据包数量异常巨大）
mininet> dpctl dump-flows
# 观察 n_packets 参数，会发现数百万个包

# 启动 Wireshark 抓包
mininet> h3 wireshark &
# 会看到大量重复的 ARP Request 包
```

**问题分析**：
- ❌ ARP 广播包在环路中无限循环
- ❌ 淹没了正常通信的数据包
- ❌ CPU 使用率极高

**清理环境：**
```bash
mininet> exit
$ sudo mn -c
```

---

#### 步骤 2：找出 s1 的端口号

**终端 1：启动控制器**
```bash
osken-manager self_learning_switch.py
```

**终端 2：启动网络拓扑**
```bash
sudo ./topo_2.py
```

**Mininet CLI 中：**
```bash
mininet> h4 ping -c 3 h2
```

**观察控制器输出**，找出 s1 (dpid=1) 连接 s3 和 s4 的端口号。

**示例输出分析**：
```
# 假设看到以下输出
dpid=1, in_port=2, ...  # s1 的端口 2 可能连接 s3
dpid=1, in_port=3, ...  # s1 的端口 3 可能连接 s4
```

记录下来：
- s1 连接 s3 的端口：`2`
- s1 连接 s4 的端口：`3`

**清理环境：**
```bash
mininet> exit
$ sudo mn -c
```

---

#### 步骤 3：修改 loop_breaker_switch.py

**编辑 `loop_breaker_switch.py` 第 79 行：**

```python
# 修改为实际端口号（例如禁用端口 2）
target_port = 2  # 根据步骤 2 的结果修改
```

---

#### 步骤 4：测试禁用端口方案

**终端 1：启动控制器**
```bash
osken-manager loop_breaker_switch.py
```

**终端 2：启动网络拓扑**
```bash
sudo ./topo_2.py
```

**Mininet CLI 中：**
```bash
# 测试连通性
mininet> h4 ping -c 10 h2
# ✅ 应该能正常通信

# 查看控制器日志
# 应该看到：Port X on switch 1 has been disabled to break the loop

# 启动 Wireshark 验证
mininet> h3 wireshark &
# ✅ 不再有环路，只有正常的 ARP 和 ICMP 包
```

---

#### 步骤 5：对比不同端口的影响

**分别禁用端口 2 和端口 3，对比通信路径的差异：**

**禁用 s1 的端口 2（连接 s3）：**
- 通信路径：h4 → s4 → s2 → h2（绕过 s3）

**禁用 s1 的端口 3（连接 s4）：**
- 通信路径：h4 → s4 → s3 → s1 → s2 → h2（绕过 s1-s4 直连）

---

### 📋 实验报告要求

#### 1. 环路问题观察（必需）

**截图和记录**：
- ✅ 运行 `self_learning_switch.py` + `topo_2.py` 的 ping 失败结果
- ✅ 控制器输出：同一个包从多个端口进入 s1（环路证据）
- ✅ Wireshark 抓包：大量重复的 ARP Request 包
- ✅ 流表查看：`dpctl dump-flows` 显示 n_packets 数量巨大

**分析说明**：
- 说明为什么会出现 "Destination Host Unreachable"
- 解释环路形成的原因（s1-s3-s4 之间的多条链路）
- 分析 ARP 广播在环路中的传播过程

#### 2. 端口号识别（必需）

**记录内容**：
```
s1 的端口映射：
- 端口 1：连接 h1（主机）
- 端口 2：连接 s2（交换机）
- 端口 3：连接 s3（交换机）
- 端口 4：连接 s4（交换机）
```

**分析方法**：
- 从控制器输出的 `dpid=1, in_port=X` 判断端口号
- 使用 `sh ovs-ofctl show s1` 命令查看端口连接信息

#### 3. 禁用端口实验（必需）

**实验记录**：

| 测试场景 | 禁用端口 | Ping 结果 | 说明 |
|---------|---------|----------|------|
| 场景 1 | 端口 3 (s1-s3) | ❌ 失败 | 环路未完全消除，s1-s2-...-s4 仍形成环路 |
| 场景 2 | 端口 4 (s1-s4) | ❌ 失败 | 环路未完全消除，s1-s3-s4 仍通过 s3-s4 直连形成环路 |

**关键发现**：
- 单一端口禁用**无法解决**此拓扑的环路问题
- 需要禁用**多个端口**或使用**更智能的方法**

#### 4. 方法局限性分析（重点！）

**为什么禁用端口方法失败了？**

1. **拓扑复杂度**：
   - topo_2.py 设计了多个相互嵌套的环路
   - s3-s4 之间有直连链路，形成独立的环路分支

2. **端口禁用的局限**：
   - 需要预先知道完整的网络拓扑
   - 在复杂环路中，可能需要禁用多个端口
   - 禁用端口会永久改变网络结构，降低冗余性

3. **实际网络场景**：
   - 生产环境中的网络拓扑往往比实验更复杂
   - 动态变化的网络需要动态的解决方案
   - 禁用端口方法不适合大规模网络

**实验设计意图**：
- 故意设计复杂拓扑，让禁用端口方法失效
- 引出任务二之二的通用解决方案

### ✅ 任务二之一验证清单

- [ ] 观察到环路问题（ping 失败，流表 n_packets 巨大）
- [ ] 找出 s1 连接 s3 和 s4 的端口号（3 和 4）
- [ ] 测试禁用端口 3 和端口 4（预期：可能都无法完全解决）
- [ ] 理解端口禁用方法的局限性
- [ ] 截图保存环路问题的各种现象

---

## 🔍 任务二之二：转发历史信息解决环路广播

### 🎯 任务目标

通过记录 ARP Request 转发历史，检测并阻断环路。

### 🌐 网络拓扑

与任务二之一相同（`topo_2.py`）。

### 🔧 实验步骤

#### 步骤 1：测试环路检测方案

**终端 1：启动控制器**
```bash
osken-manager loop_detecting_switch.py
```

**终端 2：启动网络拓扑**
```bash
sudo ./topo_2.py
```

**Mininet CLI 中：**
```bash
# 测试连通性
mininet> h4 ping -c 10 h2
# ✅ 应该能正常通信

# 启动 Wireshark 验证
mininet> h3 wireshark &
# ✅ 不再有环路
```

---

#### 步骤 2：观察控制器日志

**控制器输出示例**：

```
Recording ARP request: dpid=1, src=00:00:00:00:00:04, dst_ip=10.0.0.2, in_port=3
Recording ARP request: dpid=3, src=00:00:00:00:00:04, dst_ip=10.0.0.2, in_port=1
Loop detected! Dropping ARP request: dpid=1, src=00:00:00:00:00:04, dst_ip=10.0.0.2, in_port=2 (previous port=3)
```

**日志分析**：
1. **第一次记录**：s1 从端口 3 收到 h4 发出的 ARP Request
2. **第二次记录**：s3 从端口 1 收到相同的 ARP Request
3. **环路检测**：s1 再次从端口 2 收到相同的 ARP Request（说明环路）→ 丢弃！

---

#### 步骤 3：环路判断逻辑说明

**核心思想**：
- 维护映射表 `sw`：`(dpid, src_mac, dst_ip) -> in_port`
- 如果同一个 `(dpid, src_mac, dst_ip)` 从不同端口收到 → 检测到环路 → 丢弃

**举例说明**：

假设 h4 (MAC: `00:00:00:00:00:04`, IP: `10.0.0.4`) 要 ping h2 (IP: `10.0.0.2`)：

1. **h4 发出 ARP Request**：询问谁有 `10.0.0.2`
2. **广播传播路径**：
   ```
   h4 → s4 → s1 (端口3) → s3 (环路)
               ↓
             s2 → h2 ✅
   ```
3. **环路检测**：
   - s1 第一次从端口 3 收到 → 记录 `(1, 00:00:00:00:00:04, 10.0.0.2) -> 3`
   - s1 经过环路后从端口 2 又收到同样的包 → 检测到环路 → 丢弃！

---

### 📋 实验报告要求

#### 1. 环路检测成功验证（必需）

**截图和记录**：
```
Ping 结果：
- 10 packets transmitted, 10 received, 0% packet loss ✅
- 延迟正常（< 15ms）
```

**控制器日志示例**：
```
Recording ARP request: dpid=1, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=2
Recording ARP request: dpid=4, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=1
Loop detected! Dropping ARP request: dpid=1, src=XX:XX:XX:XX:XX:XX, dst_ip=10.0.0.2, in_port=3
Packet matched: dpid=2, src=..., in_port=1, dst=..., out_port=2
```

#### 2. 环路判断逻辑说明（重点！）

**核心思想**：
```
数据结构：self.sw = {(dpid, src_mac, dst_ip): in_port}

检测逻辑：
1. 第一次收到 ARP Request → 记录 (dpid, src_mac, dst_ip) -> in_port
2. 再次收到相同 ARP Request：
   - 如果 in_port 相同 → 重传，正常处理
   - 如果 in_port 不同 → 环路！丢弃包
```

**举例说明**（必需！）：

假设 h4 (MAC: `aa:aa:aa:aa:aa:aa`) ping h2 (IP: `10.0.0.2`)

**步骤 1**：h4 发出 ARP Request 广播
```
ARP Request: "Who has 10.0.0.2? Tell 10.0.0.4"
```

**步骤 2**：广播在网络中传播
```
h4 → s4 (port 1) → s1 (port 4)
                  ↓
记录：sw[(1, aa:aa:aa:aa:aa:aa, 10.0.0.2)] = 4
                  ↓
转发到 s2（正常路径）✅
转发到 s3（进入环路）
```

**步骤 3**：环路返回
```
s3 → s4 → s1 (port 4 再次收到)

检查：
- Key: (1, aa:aa:aa:aa:aa:aa, 10.0.0.2)
- 已存在？是
- 之前的 port: 4
- 现在的 port: 4
- 判定：相同端口，可能是重传 → 处理（实际上会再检测其他端口）

继续：
s3 → s1 (port 3 收到)

检查：
- Key: (1, aa:aa:aa:aa:aa:aa, 10.0.0.2)  
- 已存在？是
- 之前的 port: 4
- 现在的 port: 3  ← 不同！
- 判定：环路！ → 丢弃包 ❌
```

**步骤 4**：正常通信继续
```
h2 从正常路径收到 ARP Request
h2 回复 ARP Reply
h4 收到 Reply，学习到 MAC 地址
开始 ICMP ping（成功）✅
```

#### 3. 对比两种方法（重点！）

| 对比项 | 禁用端口方法 | 转发历史检测方法 |
|-------|-------------|----------------|
| **原理** | 物理断开链路 | 智能识别环路包 |
| **实现难度** | 简单（一行代码） | 中等（需要维护状态） |
| **适用场景** | 简单单环拓扑 | 复杂多环拓扑 ✅ |
| **拓扑要求** | 需预知拓扑结构 | 自动适应 ✅ |
| **对网络影响** | 永久改变结构 | 不改变物理结构 ✅ |
| **冗余性** | 降低冗余性 | 保持冗余性 ✅ |
| **可扩展性** | 难以扩展 | 容易扩展 ✅ |
| **topo_2 效果** | ❌ 失败 | ✅ 成功 |

**结论**：
- 禁用端口方法适合**简单、已知**的拓扑
- 转发历史检测方法是**更通用、智能**的解决方案
- 实际生产环境推荐使用**环路检测**或 **STP 协议**

### ✅ 任务二之二验证清单

- [ ] h4 和 h2 能正常通信（0% packet loss）
- [ ] 控制器日志显示 "Recording ARP request"
- [ ] 控制器日志显示 "Loop detected! Dropping..."
- [ ] 能够解释环路判断逻辑（用自己的话）
- [ ] 举例说明环路检测的完整过程
- [ ] 对比两种方法的优缺点

---

## 📝 实验报告撰写指南

### 📊 报告结构建议

#### 一、实验目的（1 段）
- 理解 SDN 自学习机制
- 掌握环路广播的形成原因和防治方法
- 对比不同环路解决方案的优缺点

#### 二、实验环境（表格）
```
操作系统：Ubuntu Linux (虚拟机)
工具软件：Mininet, OS-Ken, Wireshark
Python 版本：3.x
OpenFlow 版本：1.3
```

#### 三、任务一：自学习交换机（2-3 页）

**3.1 简单交换机的缺陷**
- 截图：h3 收到 h4 和 h2 之间的通信
- 说明：洪泛导致所有主机收到无关数据包

**3.2 自学习交换机实现**
- 代码核心逻辑（MAC 地址学习表）
- 控制器输出的五元组分析
- MAC 地址和端口映射表

**3.3 Wireshark 抓包分析**
- ARP 包分析（1-4 个，正常）
- ICMP 包分析（0 个或很少，成功）
- ICMPv6 包说明（系统流量，与实验无关）

**3.4 hard_timeout 参数对比**
- hard_timeout=0：永久流表
- hard_timeout=5：5 秒失效
- 对比表格和分析

#### 四、任务二之一：禁用端口（2-3 页）

**4.1 环路问题观察**
- 截图：ping 失败（Destination Host Unreachable）
- 截图：控制器输出（同一包从多个端口进入）
- 截图：Wireshark（大量重复 ARP Request）
- 截图：流表 n_packets 巨大

**4.2 端口号识别**
- s1 的端口映射表
- 识别方法说明

**4.3 禁用端口实验**
- 禁用端口 3 的结果（失败原因）
- 禁用端口 4 的结果（失败原因）

**4.4 方法局限性分析**（重点！）
- 为什么失败？
- 复杂拓扑的挑战
- 实际应用场景的限制

#### 五、任务二之二：转发历史检测（3-4 页）

**5.1 环路检测成功验证**
- 截图：ping 成功（0% loss）
- 截图：控制器日志（Recording + Loop detected）

**5.2 环路判断逻辑详解**（重点！）
- 数据结构说明
- 检测算法流程图
- 举例说明（h4 → h2 的完整过程）

**5.3 方法对比分析**
- 对比表格
- 优缺点分析
- 适用场景讨论

#### 六、实验总结（1-2 段）
- 实验收获
- 对 SDN 的理解
- 环路问题的启示

#### 七、思考题（可选）
- 如果网络拓扑有更多环路，如何扩展解决方案？
- STP 协议与本实验方法的区别？
- 如何在生产环境中部署类似机制？

---

### 📸 必需的截图清单

#### 任务一（6 张）
1. ✅ simple_switch.py 运行结果（h3 收到无关包）
2. ✅ self_learning_switch.py 控制器输出（五元组）
3. ✅ Wireshark 过滤 arp 的结果
4. ✅ Wireshark 过滤 icmp 的结果（空或很少）
5. ✅ ping 成功截图（0% loss）
6. ✅ hard_timeout=5 时的控制器输出对比

#### 任务二之一（5 张）
1. ✅ 环路问题：ping 失败截图
2. ✅ 环路问题：控制器输出（环路证据）
3. ✅ 环路问题：Wireshark 大量 ARP Request
4. ✅ 环路问题：流表 n_packets 巨大
5. ✅ ovs-ofctl show s1 的输出（端口信息）

#### 任务二之二（3 张）
1. ✅ ping 成功截图
2. ✅ 控制器日志：Recording ARP request
3. ✅ 控制器日志：Loop detected! Dropping...

---

### 📋 实验数据记录模板

#### 任务一数据记录

```
主机 MAC 地址：
- h1: __:__:__:__:__:__
- h2: __:__:__:__:__:__
- h3: __:__:__:__:__:__
- h4: __:__:__:__:__:__

通信路径（h4 → h2）：
去程：h4 → s__ (port__) → s__ (port__) → ... → h2
回程：h2 → s__ (port__) → s__ (port__) → ... → h4

hard_timeout 对比：
- hard_timeout=0：控制器输出 __ 次
- hard_timeout=5：控制器输出 __ 次（每 5 秒）
```

#### 任务二数据记录

```
端口映射：
- s1 端口 1：连接 ____
- s1 端口 2：连接 ____
- s1 端口 3：连接 ____
- s1 端口 4：连接 ____

禁用端口实验：
- 禁用端口 3：结果 ______（成功/失败），原因 ______
- 禁用端口 4：结果 ______（成功/失败），原因 ______

环路检测：
- 第一次记录：dpid=__, src=______, dst_ip=______, in_port=__
- 环路检测：dpid=__, in_port=__ (previous port=__)
- Ping 结果：__ packets transmitted, __ received, __% loss
```

---

### 💡 报告撰写技巧

1. **截图清晰**：
   - 使用虚拟机截图工具或屏幕录制
   - 标注关键信息（用红框或箭头）
   - 图片下方添加说明文字

2. **数据真实**：
   - 使用实际实验的 MAC 地址和端口号
   - 不要编造数据

3. **分析深入**：
   - 不只是描述现象，要分析原因
   - 对比实验结果，得出结论
   - 联系理论知识（ARP、MAC 学习、环路）

4. **逻辑清晰**：
   - 问题 → 方法 → 结果 → 分析
   - 使用表格、流程图等可视化工具
   - 代码关键部分加注释说明

5. **重点突出**：
   - 任务二的方法对比是报告的核心
   - ICMPv6 的说明要清楚
   - 环路检测逻辑要详细

---

## 🛠️ 常用命令速查

### Mininet CLI 命令

```bash
# 查看网络拓扑
mininet> net

# 查看所有节点
mininet> nodes

# 查看链路
mininet> links

# 主机 ping 测试
mininet> h1 ping -c 3 h2

# 测试全网连通性
mininet> pingall

# 查看所有交换机流表
mininet> dpctl dump-flows

# 启动 Wireshark
mininet> h1 wireshark &

# 退出
mininet> exit
```

### OVS 命令（在普通终端）

```bash
# 查看某个交换机的流表
sudo ovs-ofctl dump-flows s1

# 查看交换机端口信息
sudo ovs-ofctl show s1

# 查看交换机配置
sudo ovs-vsctl show
```

### 环境管理

```bash
# 激活虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 清理 Mininet
sudo mn -c
```

---

## 📊 实验报告要点

### 任务一：自学习交换机

1. **简单交换机的缺陷**：
   - 截图：h3 收到 h4 和 h2 之间的通信包
   - 说明：洪泛导致所有端口都收到包

2. **自学习交换机的改进**：
   - 截图：h3 不再收到 h4 和 h2 之间的 ICMP 包
   - 控制器日志：五元组信息

3. **MAC 地址和端口分析**：
   - 指出 h2、h4 的 MAC 地址
   - 指出它们连接的交换机和端口号

4. **hard_timeout 参数对比**：
   - `hard_timeout=0`：控制器只在学习阶段输出
   - `hard_timeout=5`：每 5 秒重新学习

### 任务二之一：禁用端口

1. **环路问题观察**：
   - 截图：流表中 n_packets 数量巨大
   - 截图：Wireshark 中大量重复 ARP Request

2. **端口号分析**：
   - 指出 s1 连接 s3 的端口号
   - 指出 s1 连接 s4 的端口号

3. **禁用端口效果**：
   - 截图：禁用后 ping 成功
   - 分析：不同端口禁用对路径的影响

### 任务二之二：转发历史检测

1. **环路检测日志**：
   - 截图：控制器输出的环路检测信息

2. **逻辑说明**：
   - 解释 `(dpid, src_mac, dst_ip) -> in_port` 映射表
   - 举例说明如何检测环路

---

## 🐛 常见问题

### 1. 虚拟环境激活失败

```bash
# 确保在 lab2 目录下
cd ~/桌面/lab/lab2

# 检查 .venv 是否存在
ls -la .venv

# 如果不存在，重新同步
uv sync
```

### 2. 拓扑文件无法运行

```bash
# 添加执行权限
chmod +x topo_1.py topo_2.py

# 检查 shebang
head -n 1 topo_1.py
# 应该是：#!/usr/bin/env python3
```

### 3. 控制器无法连接

```bash
# 确保端口 6633 未被占用
sudo netstat -tulpn | grep 6633

# 清理旧的 Mininet 进程
sudo mn -c
```

### 4. Wireshark 无法启动

```bash
# 确保安装了 Wireshark
sudo apt install wireshark

# 添加用户权限
sudo usermod -aG wireshark $USER

# 重新登录后生效
```

---

## 📚 参考资料

- [OS-Ken 官方文档](https://docs.openstack.org/os-ken/latest/)
- [Mininet 官方文档](http://mininet.org/)
- [OpenFlow 规范](https://www.opennetworking.org/software-defined-standards/specifications/)
- [SDN Lab 论坛](https://www.sdnlab.com/)

---

## ✅ 实验完成检查清单

### 任务一
- [ ] 理解简单交换机的洪泛机制
- [ ] 实现 MAC 地址自学习
- [ ] 能够分析 MAC 地址和端口映射
- [ ] 理解流表超时参数的作用

### 任务二之一
- [ ] 观察环路广播现象
- [ ] 找出交换机端口号
- [ ] 使用 OFPPortMod 禁用端口
- [ ] 分析不同端口禁用的影响

### 任务二之二
- [ ] 实现 ARP 转发历史记录
- [ ] 检测并阻断环路
- [ ] 能够解释环路检测逻辑

---

**实验完成！祝你顺利通过！** 🎉

如有问题，请查阅 [instruction.md](instruction.md) 获取更多详细信息。

