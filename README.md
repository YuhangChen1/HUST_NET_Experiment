# 🌐 计算机网络实验 Lab for 本硕博，智科，大数据

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)


> 📚 **完整的计算机网络实验集合**，涵盖网络拓扑构建、SDN 控制器、流表配置等核心内容

## ⭐ 如果这个项目对你有帮助，请给个 Star！

---

## 📂 实验内容

### Lab 1: FAT TREE 拓扑实验 ✅


👉 **[查看 Lab 1 详细指南](lab1/README.md)**

---

### Lab 2: SDN 自学习与环路检测实验 ✅

**核心内容**：基于 OpenFlow/OS-Ken 控制器实现交换机自学习和环路广播防治

**技术栈**：
- 🎮 **OS-Ken 控制器** - OpenFlow SDN 控制器
- 🔧 **Mininet** - 网络仿真器
- 🌐 **OpenFlow 1.3** - 南向接口协议
- 📊 **Wireshark** - 数据包分析



👉 **[查看 Lab 2 详细指南](lab2/README.md)**

---

### Lab 3: SDN 链路选择与故障恢复实验 ✅
👉 **[查看 Lab 3 详细指南](lab3/README.md)**

1. 📖 先阅读 [QUICKSTART.md](lab3/QUICKSTART.md) 快速上手
2. 🔧 必读 [OSKEN_MODIFICATION.md](lab3/OSKEN_MODIFICATION.md) 修改 OS-Ken 源文件
3. 📝 查看 [CHANGES_SUMMARY.md](lab3/CHANGES_SUMMARY.md) 了解代码修改
4. 📋 使用 [REPORT_TEMPLATE.md](lab3/REPORT_TEMPLATE.md) 撰写报告

**核心内容**：通过 LLDP 协议实现链路发现和时延测量，实现动态路径选择和故障容错

**技术栈**：
- 📡 **LLDP 协议** - 链路层发现协议
- 🎮 **OS-Ken 控制器** - OpenFlow SDN 控制器
- 📊 **NetworkX** - 图算法库
- ⏱️ **Echo 消息** - 时延测量
- 🔧 **Mininet** - 网络仿真器

**实验任务**：
1. **任务一**：基于最少跳数的路径选择
   - 理解 LLDP 拓扑发现机制
   - 使用 NetworkX 计算最短路径
   - 处理 ARP 环路问题

2. **任务二**：基于最小时延的路径选择
   - LLDP 时延测量（T<sub>lldp</sub>）
   - Echo RTT 测量（T<sub>echo</sub>）
   - 计算链路单向时延
   - 动态选择最优路径

3. **任务三**：链路故障容忍与自动恢复
   - 捕获 `EventOFPPortStatus` 事件
   - 自动检测链路故障
   - 动态切换备用路径
   - 故障恢复后自动回切

**Lab 3 结构：**
```
lab3/
├── README.md                   # 📘 详细的实验指南（1351 行）
├── QUICKSTART.md               # 🚀 快速开始指南（3 个任务的运行步骤）
├── OSKEN_MODIFICATION.md       # 🔧 OS-Ken 源文件修改说明
├── CHANGES_SUMMARY.md          # 📝 代码修改详细总结
├── COMPLETION_SUMMARY.md       # ✅ 完成情况总结和代码统计
├── REPORT_TEMPLATE.md          # 📋 实验报告模板（含思考题）
├── least_hops.py               # ✅ 任务一：最少跳数路径
├── shortest_delay.py           # ✅ 任务二+三：最小时延路径和故障容忍
├── network_awareness.py        # 📡 拓扑发现和链路时延测量
├── topo.py                     # 🌐 实验拓扑（9 台交换机）
└── setup.sh                    # 🔨 环境设置脚本
```

## 🚀 快速开始

### 环境要求

```bash
# 操作系统
Ubuntu 18.04 / 20.04 / 22.04 (推荐使用虚拟机)

# 必需软件
- Python 3.6+
- Mininet 2.3.0+
- Open vSwitch 2.9.0+
```

### 安装 Mininet

```bash
# 方法 1：使用官方脚本（推荐）
git clone https://github.com/mininet/mininet
cd mininet
git checkout 2.3.0
./util/install.sh -a

# 方法 2：使用 apt（Ubuntu）
sudo apt update
sudo apt install mininet openvswitch-switch
```

### 克隆本仓库

```bash
git clone https://github.com/yourusername/lab.git
cd lab
```

### 运行实验

**Lab 1（FAT TREE 拓扑）：**
```bash
cd lab1
sudo python3 fat_tree_topo.py
```
🎉 **30 秒后看到 pingall 成功！**

**Lab 2（SDN 自学习）：**
```bash
cd lab2
source setup.sh  # 一键设置环境
# 终端 1：
osken-manager self_learning_switch.py
# 终端 2：
sudo ./topo_1.py
```
🎉 **实现交换机自学习功能！**

**Lab 3（链路选择与故障恢复）：**
```bash
cd lab3
source setup.sh  # 一键设置环境

# 任务一：最少跳数路径
# 终端 1：
sudo ./topo.py
# 终端 2：
uv run osken-manager least_hops.py --observe-links
# Mininet: h2 ping h9

# 任务二+三：最小时延路径和故障容忍
# 终端 1：
sudo ./topo.py
# 终端 2：
uv run osken-manager shortest_delay.py --observe-links
# Mininet: h2 ping h9
# Mininet: link s6 s7 down  (测试故障切换)
# Mininet: link s6 s7 up    (测试故障恢复)
```
🎉 **实现动态路径选择和自动故障恢复！**

---

## 📖 使用指南

每个实验文件夹都包含：

**Lab 1 结构：**
```
lab1/
├── README.md              # 📘 详细的实验指南
├── fat_tree_topo.py       # ✅ 完整工作版本
├── fat_tree_topo_4_bad.py # ❌ 问题演示版本
├── debug.py               # 🔧 调试版本
└── [其他辅助文件]
```

**Lab 2 结构：**
```
lab2/
├── README.md                   # 📘 详细的实验指南
├── setup.sh                    # 🚀 一键环境设置脚本
├── simple_switch.py            # 📦 简单交换机（洪泛）
├── self_learning_switch.py     # ✅ 自学习交换机
├── loop_breaker_switch.py      # 🔧 端口禁用解决环路
├── loop_detecting_switch.py    # 🔍 转发历史检测环路
├── topo_1.py                   # 🌐 无环路拓扑
├── topo_2.py                   # 🔁 有环路拓扑
└── instruction.md              # 📖 详细操作指南
```

**Lab 3 结构：**
```
lab3/
├── README.md                   # 📘 详细的实验指南（1351 行）
├── QUICKSTART.md               # 🚀 快速开始指南（3 个任务的运行步骤）
├── OSKEN_MODIFICATION.md       # 🔧 OS-Ken 源文件修改说明
├── CHANGES_SUMMARY.md          # 📝 代码修改详细总结
├── COMPLETION_SUMMARY.md       # ✅ 完成情况总结和代码统计
├── REPORT_TEMPLATE.md          # 📋 实验报告模板（含思考题）
├── least_hops.py               # ✅ 任务一：最少跳数路径
├── shortest_delay.py           # ✅ 任务二+三：最小时延路径和故障容忍
├── network_awareness.py        # 📡 拓扑发现和链路时延测量
├── topo.py                     # 🌐 实验拓扑（9 台交换机）
└── setup.sh                    # 🔨 环境设置脚本
```

**请务必先阅读各个实验的 README.md 文件！**

里面包含：
- ✅ 详细的实验步骤
- 📊 数据收集方法
- 🐛 常见问题及解决方案
- 📸 实验报告模板
- 🎯 演示技巧

---

<!-- ## 📝 实验报告要点

### Lab 1: FAT TREE 拓扑实验报告

详见 [lab1/README.md](lab1/README.md)，包含：
- 拓扑结构分析（16 主机，20 交换机）
- STP 生成树分析
- MAC 地址学习表
- 跨 Pod 通信路径分析

### Lab 2: SDN 自学习与环路检测报告指导
详见 [lab2/README.md](lab2/README.md)
#### 📊 任务一：自学习交换机

**1. MAC 地址和端口映射**

根据控制器输出分析：
```
示例输出：
Packet matched: dpid=2, src=26:47:73:73:99:55, in_port=1, dst=1a:4c:a8:73:10:31, out_port=2
Packet matched: dpid=1, src=26:47:73:73:99:55, in_port=2, dst=1a:4c:a8:73:10:31, out_port=4
Packet matched: dpid=4, src=26:47:73:73:99:55, in_port=2, dst=1a:4c:a8:73:10:31, out_port=1
```

**分析要点**：
- 主机 MAC 地址识别（从 src 和 dst 字段）
- 通信路径追踪（按 dpid 和端口顺序）
- 端口映射关系（主机连接的交换机端口）

**2. Wireshark 抓包分析**

**正确的实验现象**：

在 h3 的 Wireshark 中过滤数据包：

| 过滤器 | 预期结果 | 说明 |
|--------|---------|------|
| `arp` | 1-4 个包 | ARP 广播正常，MAC 地址学习 |
| `icmp` | 0 个或 1-2 个包 | ✅ h3 不收到 h4↔h2 的 ping 包，自学习成功 |
| `icmp6` | 10+ 个包 | IPv6 系统流量（正常，可忽略）|

**⚠️ ICMPv6 说明（重要）**：

- **icmp6 ≠ icmp**
- **icmp6** 是 IPv6 的 ICMP 协议，包含：
  - Router Solicitation（路由器请求）
  - Neighbor Solicitation（邻居发现）
  - Multicast Listener Report（组播监听）
- 这些是 **Linux 系统自动发送的 IPv6 协议包**，与实验的 IPv4 通信无关
- **判断自学习是否成功，应该看 `icmp`（IPv4）过滤结果，而不是 `icmp6`**

**截图要求**：
1. 控制器输出（五元组信息）
2. Wireshark 过滤 `icmp` 的结果（应为空或很少）
3. Wireshark 过滤 `arp` 的结果（显示 MAC 学习过程）
4. ping 成功截图（0% packet loss）

**3. hard_timeout 参数对比**

| 参数值 | 控制器输出规律 | 原因分析 |
|--------|--------------|---------|
| `hard_timeout=0` | 只在学习阶段输出，之后无输出 | 流表永久有效，交换机直接转发 |
| `hard_timeout=5` | 每 5 秒重新输出日志 | 流表 5 秒后失效，需重新学习 |

**4. 通信路径分析**

示例：h4 → h2 的通信路径

**去程（Request）**：
```
h4 → s4 (dpid=4, in_port=1 → out_port=2)
   → s1 (dpid=1, in_port=4 → out_port=2)
   → s2 (dpid=2, in_port=2 → out_port=1)
   → h2
```

**回程（Reply）**：
```
h2 → s2 (dpid=2, in_port=1 → out_port=2)
   → s1 (dpid=1, in_port=2 → out_port=4)
   → s4 (dpid=4, in_port=2 → out_port=1)
   → h4
```

---

#### 🔁 任务二之一：禁用端口解决环路

**1. 环路问题观察**

**错误现象**（使用 self_learning_switch.py + topo_2.py）：
- ping 失败或延迟极高（>1000ms）
- 流表 `n_packets` 数量巨大（数百万）
- Wireshark 中大量重复的 ARP Request 包
- CPU 使用率极高

**原因分析**：
- topo_2.py 在 s1、s3、s4 之间形成环路
- ARP 广播包在环路中无限循环
- 淹没了正常通信的数据包

**2. 端口号识别**

**方法**：运行 self_learning_switch.py + topo_2.py，观察控制器输出

示例：
```
dpid=1, in_port=2, ...  # s1 的端口 2 连接 s3
dpid=1, in_port=3, ...  # s1 的端口 3 连接 s4
```

记录：
- s1 连接 s3 的端口：`__`（填写实际端口号）
- s1 连接 s4 的端口：`__`（填写实际端口号）

**3. 禁用端口效果**

**实验步骤**：
1. 修改 `loop_breaker_switch.py` 第 79 行 `target_port` 为实际端口号
2. 运行 loop_breaker_switch.py + topo_2.py
3. 执行 `h4 ping h2`，验证通信成功

**不同端口禁用的影响**：

| 禁用端口 | 断开的链路 | 通信路径变化 |
|---------|-----------|-------------|
| s1 的端口 2 | s1 ↔ s3 | h4 → s4 → s2 → h2（绕过 s3）|
| s1 的端口 3 | s1 ↔ s4 | h4 → s4 → s3 → s1 → s2 → h2（绕过 s1-s4 直连）|

---

#### 🔍 任务二之二：转发历史检测环路

**1. 环路检测逻辑**

**核心思想**：
- 维护映射表 `sw`：`(dpid, src_mac, dst_ip) -> in_port`
- 如果同一个 `(dpid, src_mac, dst_ip)` 从不同端口收到 → 检测到环路 → 丢弃

**2. 控制器日志分析**

示例输出：
```
Recording ARP request: dpid=1, src=00:00:00:00:00:04, dst_ip=10.0.0.2, in_port=3
Recording ARP request: dpid=3, src=00:00:00:00:00:04, dst_ip=10.0.0.2, in_port=1
Loop detected! Dropping ARP request: dpid=1, src=00:00:00:00:00:04, dst_ip=10.0.0.2, in_port=2 (previous port=3)
```

**日志含义**：
1. **第一次记录**：s1 从端口 3 收到 h4 发出的 ARP Request（询问 10.0.0.2）
2. **第二次记录**：s3 从端口 1 收到相同的 ARP Request
3. **环路检测**：s1 再次从端口 2 收到相同的 ARP Request → 检测到环路 → 丢弃！

**3. 举例说明**

假设 h4 (MAC: `00:00:00:00:00:04`, IP: `10.0.0.4`) 要 ping h2 (IP: `10.0.0.2`)：

**步骤 1**：h4 发出 ARP Request 广播，询问谁有 `10.0.0.2`

**步骤 2**：广播传播路径
```
h4 → s4 → s1 (端口 3) → s3 → s1 (端口 2，环路！)
              ↓
            s2 → h2 ✅
```

**步骤 3**：环路检测过程
- s1 第一次从端口 3 收到 → 记录 `(1, 00:00:00:00:00:04, 10.0.0.2) -> 3`
- 包经过 s3 后，s1 从端口 2 又收到同样的包
- 检测到 `(1, 00:00:00:00:00:04, 10.0.0.2)` 已存在，但端口不同（2 ≠ 3）
- **判定为环路** → 丢弃包，不再转发

---

#### ✅ 实验报告检查清单

**任务一：自学习交换机**
- [ ] 截图：控制器输出五元组信息
- [ ] 截图：Wireshark 过滤 `icmp` 的结果（应为空）
- [ ] 截图：Wireshark 过滤 `arp` 的结果
- [ ] 说明：ICMPv6 与实验无关的解释
- [ ] 分析：h2 和 h4 的 MAC 地址
- [ ] 分析：通信路径（去程和回程）
- [ ] 对比：hard_timeout=0 vs hard_timeout=5 的输出差异

**任务二之一：禁用端口**
- [ ] 截图：环路问题（流表 n_packets 巨大）
- [ ] 截图：Wireshark 中大量重复 ARP Request
- [ ] 分析：s1 连接 s3 和 s4 的端口号
- [ ] 截图：禁用端口后 ping 成功
- [ ] 分析：不同端口禁用对通信路径的影响

**任务二之二：转发历史检测**
- [ ] 截图：控制器输出的环路检测日志
- [ ] 说明：环路检测逻辑（映射表机制）
- [ ] 举例：具体的环路检测过程
- [ ] 截图：ping 成功（无环路） -->

<!-- ---

## 💡 Lab 2 思考题解答

### 思考题 1：如果网络拓扑有更多环路，如何扩展解决方案？

**答案：扩展转发历史检测方法（推荐）**

当前实现已经具有很好的扩展性：
```python
self.sw = {(dpid, src_mac, dst_ip): in_port}
```

**核心优势**：
- ✅ **无需修改代码**：当前方法自动适应任意复杂度的环路
- ✅ **自动记录所有交换机的 ARP 转发历史**
- ✅ **可以检测任意数量的嵌套环路**

**扩展方向**：

**1. 添加超时清理机制**
```python
class EnhancedLoopDetector:
    def __init__(self):
        self.sw = {}  # 环路检测表
        self.sw_timestamp = {}  # 记录时间戳
        
    def cleanup_expired(self):
        """定期清理过期条目，防止内存溢出"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.sw_timestamp.items()
            if current_time - v > 300  # 5分钟超时
        ]
        for key in expired_keys:
            del self.sw[key]
            del self.sw_timestamp[key]
```

**2. 扩展到其他广播协议**
```python
# 不仅检测 ARP Request，还可以检测：
- DHCP 广播
- 未知单播（unknown unicast flooding）
- 组播数据包（multicast）
- IPv6 邻居发现（Neighbor Discovery）
```

**3. 添加统计和告警**
```python
self.loop_count = {}  # 统计每个交换机的环路次数
self.loop_history = []  # 记录环路历史

def check_loop_threshold(self, dpid):
    """当环路次数过多时，触发告警"""
    if self.loop_count[dpid] > 100:
        self.send_alert(f"Switch {dpid} detected {self.loop_count[dpid]} loops!")
        # 可选：自动禁用问题端口
```

**4. 结合 STP 协议**

在生产环境中，可以分层使用：
- **STP**：物理层面消除环路，建立无环拓扑
- **环路检测**：应用层面监控和告警

**5. 引入 SDN 集中式管理**
```python
import networkx as nx

# 控制器维护全局拓扑图
topology_graph = nx.Graph()

# 检测环路
cycles = nx.simple_cycles(topology_graph)

# 智能选择要禁用的链路
# 基于负载、链路质量、冗余度等因素
for cycle in cycles:
    best_link_to_block = select_optimal_link(cycle)
    disable_link(best_link_to_block)
```

---

### 思考题 2：STP 协议与本实验方法的区别？

**详细对比表**：

| 对比项 | STP（生成树协议） | 本实验方法（转发历史检测） |
|-------|-----------------|------------------------|
| **工作层次** | 数据链路层（L2） | 应用层（SDN 控制器） |
| **实现位置** | 交换机内部 | SDN 控制器 |
| **环路处理** | 物理阻塞端口 | 智能丢弃重复包 |
| **拓扑感知** | 分布式（BPDU 交换）| 集中式（控制器全知） |
| **收敛时间** | 较慢（30-50秒）| 实时（毫秒级）✅ |
| **网络影响** | 改变物理拓扑 | 不改变物理结构 ✅ |
| **冗余性** | 降低（阻塞备用链路）| 保持（链路仍可用）✅ |
| **可编程性** | 固定算法 | 灵活可定制 ✅ |
| **部署复杂度** | 简单（自动运行）| 需要控制器支持 |
| **故障恢复** | 需要重新计算（30秒）| 立即适应 ✅ |
| **负载均衡** | 不支持 | 可以实现 ✅ |

**详细说明**：

**1. STP 工作原理**：
```
步骤 1：选举根桥（Root Bridge）
  - 所有交换机发送 BPDU（Bridge Protocol Data Unit）
  - 比较 Bridge ID（优先级 + MAC 地址）
  - Bridge ID 最小的成为根桥

步骤 2：计算到根桥的最短路径
  - 每个交换机计算到根桥的路径成本
  - 选择最小成本路径

步骤 3：确定端口角色
  - Root Port（根端口）：到根桥的最短路径
  - Designated Port（指定端口）：负责转发
  - Blocked Port（阻塞端口）：不转发数据

步骤 4：定期发送 BPDU
  - 默认每 2 秒发送一次
  - 监控拓扑变化

步骤 5：拓扑变化时重新计算
  - 需要 30-50 秒收敛
  - 期间可能导致网络中断
```

**2. 本实验方法（转发历史检测）**：
```
步骤 1：记录 ARP Request 的转发历史
  sw[(dpid, src_mac, dst_ip)] = in_port

步骤 2：检测同一请求从不同端口到达
  if key in sw and sw[key] != in_port:
      # 检测到环路

步骤 3：识别环路后丢弃重复包
  return  # 不转发

步骤 4：正常通信不受影响
  - 非环路包正常转发
  - 实时响应（毫秒级）

步骤 5：自动适应拓扑变化
  - 无需重新计算
  - 立即生效
```

**3. Lab 1 中的 STP 应用**：
- Lab 1 使用 OVS 的 STP 实现
- 消除 FAT TREE 中的环路（16主机, 20交换机）
- 物理上阻塞端口，建立树形拓扑
- 收敛时间约 30 秒

**4. Lab 2 中的创新方法**：
- 不使用 STP，在控制器层面检测
- 保留物理冗余，提高可靠性
- 更灵活，可以根据需求定制策略
- 可以实现负载均衡（STP 不能）

**实际应用场景对比**：

| 场景 | 推荐方案 | 原因 |
|-----|---------|------|
| 传统网络（无 SDN）| STP | 简单、标准、自动运行 |
| 小型网络（< 10 交换机）| STP 或 RSTP | 成本低，易部署 |
| 数据中心网络 | SDN 环路检测 | 需要低延迟，高可用 |
| 云计算环境 | SDN + TRILL/SPB | 大规模，需要多路径 |
| 混合网络 | STP + SDN | 渐进式升级 |

**结论**：
- **STP** 适合传统网络，简单可靠，但收敛慢
- **SDN 方法** 更灵活智能，适合现代数据中心，响应快
- **实际生产** 常结合使用：STP 作为底层保障，SDN 提供高级功能

---

### 思考题 3：如何在生产环境中部署类似机制？

**完整的生产级部署方案**

#### 1. 架构设计

```
┌─────────────────────────────────────────┐
│      SDN 控制器集群（高可用）               │
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │主控制器│  │备控制器│  │备控制器│          │
│  │Master │  │Backup│  │Backup│          │
│  └───┬──┘  └───┬──┘  └───┬──┘          │
│      │         │         │              │
│      └─────────┴─────────┘              │
│         │ OpenFlow 1.3                  │
└─────────┼───────────────────────────────┘
          │
┌─────────┴───────────────────────────────┐
│      核心交换机层（OVS/硬件）              │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐       │
│  │ c1 │──│ c2 │──│ c3 │──│ c4 │       │
│  └─┬──┘  └─┬──┘  └─┬──┘  └─┬──┘       │
│    │       │       │       │           │
└────┼───────┼───────┼───────┼───────────┘
     │       │       │       │
┌────┴───────┴───────┴───────┴───────────┐
│        聚合/接入交换机层                  │
│    [Pod 0]  [Pod 1]  [Pod 2]  [Pod 3]  │
│    ┌────┐  ┌────┐  ┌────┐  ┌────┐     │
│    │ a0 │  │ a1 │  │ a2 │  │ a3 │     │
│    └────┘  └────┘  └────┘  └────┘     │
└──────────────────────────────────────────┘
```

#### 2. 部署步骤

**阶段 1：测试环境验证（1-2周）**

```bash
# 1. 小规模测试
环境：2-4 台交换机，10-20 台主机
目标：
  - 验证功能正确性
  - 测试环路检测准确率（> 99.9%）
  - 压力测试（1000+ ARP/秒）

# 2. 性能基准测试
指标：
  - 控制器 CPU 占用 < 50%
  - 内存占用 < 2GB
  - 响应延迟 < 10ms
  - 吞吐量 > 10000 pps

# 3. 故障场景测试
  - 控制器故障切换
  - 交换机断链恢复
  - 大规模 ARP 风暴
```

**阶段 2：生产环境准备（2-4周）**

```python
# 生产级代码框架
from os_ken.base import app_manager
import time
import logging
from collections import defaultdict
from threading import Thread, Lock

class ProductionLoopDetector(app_manager.OSKenApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 核心数据结构
        self.sw = {}  # 环路检测: (dpid, src_mac, dst_ip) -> in_port
        self.sw_timestamp = {}  # 时间戳
        self.mac_to_port = defaultdict(dict)  # 自学习
        self.lock = Lock()  # 线程安全
        
        # 监控和统计
        self.stats = {
            'loop_detected': 0,
            'packets_dropped': 0,
            'arp_processed': 0,
            'total_packets': 0
        }
        
        # 配置参数
        self.config = {
            'entry_timeout': 300,  # 5分钟
            'cleanup_interval': 60,  # 1分钟清理一次
            'max_entries': 100000,  # 最大条目数
            'alert_threshold': 100,  # 告警阈值
            'enable_metrics': True  # 启用指标收集
        }
        
        # 启动后台任务
        self.start_background_tasks()
    
    def start_background_tasks(self):
        """启动后台维护任务"""
        # 定期清理过期条目
        cleanup_thread = Thread(
            target=self._cleanup_loop,
            daemon=True,
            name='cleanup_thread'
        )
        cleanup_thread.start()
        
        # 定期导出指标
        if self.config['enable_metrics']:
            metrics_thread = Thread(
                target=self._metrics_loop,
                daemon=True,
                name='metrics_thread'
            )
            metrics_thread.start()
    
    def _cleanup_loop(self):
        """定期清理过期条目"""
        while True:
            try:
                time.sleep(self.config['cleanup_interval'])
                self.cleanup_expired_entries()
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")
    
    def cleanup_expired_entries(self):
        """清理过期的环路检测条目"""
        with self.lock:
            current_time = time.time()
            timeout = self.config['entry_timeout']
            
            expired_keys = [
                k for k, v in self.sw_timestamp.items()
                if current_time - v > timeout
            ]
            
            for key in expired_keys:
                del self.sw[key]
                del self.sw_timestamp[key]
            
            if expired_keys:
                self.logger.info(
                    f"Cleaned up {len(expired_keys)} expired entries"
                )
    
    def _metrics_loop(self):
        """定期导出指标到监控系统"""
        while True:
            try:
                time.sleep(60)  # 每分钟导出一次
                self.export_metrics()
            except Exception as e:
                self.logger.error(f"Metrics export error: {e}")
    
    def export_metrics(self):
        """导出指标到 Prometheus/Grafana"""
        metrics = {
            'timestamp': time.time(),
            'loop_detected_total': self.stats['loop_detected'],
            'packets_dropped_total': self.stats['packets_dropped'],
            'arp_processed_total': self.stats['arp_processed'],
            'sw_entries_current': len(self.sw),
            'memory_usage_bytes': self.get_memory_usage()
        }
        
        # 发送到监控系统
        # self.send_to_prometheus(metrics)
        self.logger.info(f"Metrics: {metrics}")
    
    def detect_loop(self, dpid, src_mac, dst_ip, in_port):
        """环路检测核心逻辑"""
        key = (dpid, src_mac, dst_ip)
        
        with self.lock:
            if key in self.sw:
                if self.sw[key] != in_port:
                    # 检测到环路
                    self.stats['loop_detected'] += 1
                    self.stats['packets_dropped'] += 1
                    
                    # 告警判断
                    if (self.stats['loop_detected'] % 
                        self.config['alert_threshold'] == 0):
                        self.send_alert(
                            f"High loop rate: {self.stats['loop_detected']}",
                            level='warning'
                        )
                    
                    self.logger.info(
                        f"Loop detected: dpid={dpid}, src={src_mac}, "
                        f"dst_ip={dst_ip}, in_port={in_port} "
                        f"(previous={self.sw[key]})"
                    )
                    return True  # 环路
            else:
                # 首次记录
                self.sw[key] = in_port
                self.sw_timestamp[key] = time.time()
                self.stats['arp_processed'] += 1
        
        return False  # 非环路
    
    def send_alert(self, message, level='info'):
        """发送告警到监控系统"""
        alert = {
            'timestamp': time.time(),
            'level': level,
            'message': message,
            'source': 'SDN_Loop_Detector',
            'stats': self.stats.copy()
        }
        
        # 集成告警系统
        # - 发送到 Slack
        # - 发送到 Email
        # - 发送到 PagerDuty
        self.logger.warning(f"ALERT [{level}]: {message}")
    
    def get_memory_usage(self):
        """获取内存使用情况"""
        import sys
        return (sys.getsizeof(self.sw) + 
                sys.getsizeof(self.sw_timestamp) +
                sys.getsizeof(self.mac_to_port))
```

**阶段 3：监控和告警（持续）**

```python
# 关键指标监控
class MonitoringMetrics:
    # 性能指标
    loop_detection_rate = Gauge('loop_detection_rate', 'Loops/second')
    arp_processing_latency = Histogram('arp_latency', 'ARP processing time')
    memory_usage = Gauge('memory_usage_bytes', 'Memory usage')
    
    # 业务指标
    total_loops = Counter('total_loops_detected', 'Total loops')
    packets_dropped = Counter('packets_dropped', 'Packets dropped')
    
    # 健康指标
    controller_uptime = Gauge('controller_uptime', 'Uptime seconds')
    error_rate = Gauge('error_rate', 'Errors/minute')

# Grafana 仪表板配置
dashboard_panels = [
    {
        'title': '环路检测率',
        'metric': 'loop_detection_rate',
        'alert_threshold': 10  # 每秒超过10个环路告警
    },
    {
        'title': 'ARP 处理延迟',
        'metric': 'arp_processing_latency',
        'alert_threshold': 50  # 超过50ms告警
    },
    {
        'title': '内存使用',
        'metric': 'memory_usage_bytes',
        'alert_threshold': 2 * 1024**3  # 超过2GB告警
    }
]
```

#### 3. 最佳实践

**a. 分层防御策略**：
```
第 1 层：物理层 - STP/RSTP（传统交换机）
  作用：基础防护，确保底线安全
  
第 2 层：控制层 - SDN 环路检测（本实验方法）
  作用：智能检测，实时响应
  
第 3 层：监控层 - 实时告警和日志分析
  作用：预警，追踪，审计
```

**b. 渐进式部署**：
```
阶段 1：非核心区域（测试环境）
  - 验证功能
  - 收集数据
  - 调优参数

阶段 2：生产网络边缘
  - 小流量区域
  - 非关键业务
  - 保留回退方案

阶段 3：核心网络
  - 大流量区域
  - 关键业务
  - 7x24 监控

阶段 4：全面部署
  - 覆盖所有区域
  - 关闭传统 STP（可选）
  - 持续优化
```

**c. 故障应对策略**：
```python
class FailoverStrategy:
    def handle_controller_failure(self):
        """控制器故障处理"""
        # 1. 自动切换到备用控制器
        backup_controller.takeover()
        
        # 2. 交换机降级为 standalone 模式
        for switch in switches:
            switch.set_fail_mode('standalone')
        
        # 3. 或回退到 STP 模式
        for switch in switches:
            switch.enable_stp()
        
        # 4. 发送告警
        alert.send('Controller failover executed')
    
    def handle_switch_failure(self, switch_id):
        """交换机故障处理"""
        # 1. 从拓扑中移除
        topology.remove_switch(switch_id)
        
        # 2. 清理相关流表
        self.cleanup_switch_data(switch_id)
        
        # 3. 重新计算路径
        topology.recalculate_paths()
    
    def handle_network_partition(self):
        """网络分区处理"""
        # 1. 检测分区
        partitions = topology.detect_partitions()
        
        # 2. 每个分区独立运行
        for partition in partitions:
            partition.run_independently()
        
        # 3. 分区愈合后合并状态
        if partitions_healed():
            merge_partition_states()
```

#### 4. 部署检查清单

**部署前**：
- [ ] 完成功能测试（通过率 > 99%)
- [ ] 完成性能测试（满足 SLA 要求）
- [ ] 完成故障测试（恢复时间 < 1秒）
- [ ] 准备回退方案
- [ ] 团队培训完成

**部署中**：
- [ ] 分阶段部署（先边缘后核心）
- [ ] 实时监控关键指标
- [ ] 准备应急响应团队
- [ ] 保持通信畅通

**部署后**：
- [ ] 7x24 监控（至少前2周）
- [ ] 收集性能数据
- [ ] 优化配置参数
- [ ] 文档和培训
- [ ] 定期审查和改进

#### 5. 成本效益分析

| 项目 | 传统 STP | SDN 环路检测 | 节省/提升 |
|-----|---------|-------------|---------|
| 硬件成本 | $100K | $80K | -20% |
| 部署时间 | 2周 | 4周 | +100% |
| 收敛时间 | 30秒 | 10ms | **-99.97%** ⭐ |
| 故障恢复 | 30秒 | 实时 | **99.97%** ⭐ |
| 运维复杂度 | 低 | 中 | +50% |
| 可编程性 | 无 | 高 | **无限** ⭐ |
| 负载均衡 | 不支持 | 支持 | **新功能** ⭐ |

**ROI 分析**：
- **初期投资**：高 20%（开发 + 培训）
- **长期收益**：网络中断减少 99%，业务连续性提升
- **回本周期**：6-12 个月

---

## 🎯 总结

三个思考题的核心要点：

1. **扩展性**：转发历史检测方法天然支持复杂拓扑，只需添加监控和优化
2. **对比 STP**：SDN 方法更快更灵活，但 STP 更简单，可以结合使用
3. **生产部署**：需要完整的架构设计、分阶段部署、持续监控

这些解答展示了：
- 从实验到生产的完整路径
- SDN 技术的实际应用价值
- 网络工程的最佳实践 -->

---

<!-- ## 🎯 实验特色

### 1. 多版本脚本设计

每个实验提供 **3 个版本**：

| 版本 | 用途 | 适合场景 |
|------|------|----------|
| 完整版 | 自动配置，一键成功 | 快速验证，最终演示 |
| 问题版 | 展示常见错误 | 学习排查过程，理解原理 |
| 调试版 | 手动配置测试 | 深入学习，自主探索 | -->

<!-- ### 2. 完整的问题诊断流程

不只是"能跑的代码"，更重要的是：
- 🔍 **为什么会失败？** - 深入分析根本原因
- 🛠️ **如何诊断？** - 提供完整的调试命令
- ✅ **如何解决？** - 逐步解决每个问题
- 📚 **背后原理？** - 解释技术细节 -->

<!-- ### 3. 实验报告模板

每个实验都提供：
- 📝 完整的报告结构
- 📊 数据收集方法
- 📸 截图建议
- 💡 分析思路 -->

---

## 🤝 贡献指南

欢迎贡献！可以通过以下方式参与：

1. 🐛 **报告 Bug**：发现问题请提 Issue
2. 💡 **提出建议**：改进想法请提 Issue
3. 🔧 **提交代码**：欢迎 Pull Request
4. 📖 **完善文档**：改进 README 或注释
5. ⭐ **给个 Star**：这是对我们最大的鼓励！

### 提交 Pull Request

```bash
# 1. Fork 本仓库
# 2. 创建你的分支
git checkout -b feature/amazing-feature

# 3. 提交改动
git commit -m "Add some amazing feature"

# 4. 推送到分支
git push origin feature/amazing-feature

# 5. 提交 Pull Request
```

---

## 📚 学习资源

### 推荐阅读

- 📖 [Mininet 官方文档](http://mininet.org/)
- 📖 [Open vSwitch 文档](https://www.openvswitch.org/)
- 📄 [FAT TREE 原始论文](https://cseweb.ucsd.edu/~vahdat/papers/sigcomm08.pdf)
- 📘 [SDN 权威指南](https://github.com/SDN-Guide)

### 视频教程

- 🎥 [Mininet 入门教程](https://www.youtube.com/results?search_query=mininet+tutorial)
- 🎥 [SDN 基础课程](https://www.youtube.com/results?search_query=sdn+tutorial)

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
```

---

## 💬 联系方式

有问题或建议？

计算机学院都知道我是谁吧（

---

## 🌟 Star History

如果这个项目帮助到了你，请点击右上角的 ⭐ **Star** 按钮！

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/lab&type=Date)](https://star-history.com/#yourusername/lab&Date)

<!-- --- -->

<!-- ## 📊 项目统计

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/lab)
![GitHub issues](https://img.shields.io/github/issues/yourusername/lab)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/lab)
![GitHub contributors](https://img.shields.io/github/contributors/yourusername/lab)

--- -->

<div align="center">

### ⭐ 如果觉得有用，别忘了给个 Star！⭐

**[⬆ 回到顶部](#-计算机网络实验-lab)**

Made with ❤️ by Network Lab Team

</div>

