# FAT TREE 拓扑实验演示指南

## 📁 文件说明

本实验包含三个版本的脚本：

| 文件名 | 说明 | 用途 |
|--------|------|------|
| `fat_tree_topo.py` | ✅ **完整工作版本** | 自动配置 standalone + STP，pingall 直接成功 |
| `fat_tree_topo_4_bad.py` | ❌ **问题演示版本** | 不配置交换机，用于展示问题排查过程 |
| `debug.py` | 🔧 **调试版本** | 直接进入 CLI，不自动执行 pingall |

---

## 🎯 演示方法选择

### 方法 A：完整自动运行（推荐用于最终演示）

**适用场景**：快速展示成功结果，验证配置正确性

#### 步骤 1：清理环境
```bash
# 如果在 Mininet CLI 中，先退出
exit

# 清理之前的网络状态
sudo mn -c
```

#### 步骤 2：运行完整版脚本
```bash
cd ~/桌面/lab/lab1
sudo python3 fat_tree_topo.py
```

#### 自动执行流程
脚本会自动完成以下操作：
- ✅ 创建 k=4 的 FAT TREE 拓扑（16 主机，20 交换机）
- ✅ 设置所有交换机为 **standalone 模式**（L2 自学习）
- ✅ 启用 **STP**（生成树协议）防止广播风暴
- ✅ 等待 **30 秒** 让 STP 收敛
- ✅ 自动执行 **pingall** 测试

#### 步骤 3：验证结果
在 Mininet CLI 中查看：
```bash
# 应该显示：*** Results: 0% dropped (240/240 received)
pingall

# 查看网络拓扑
net

# 查看所有节点
nodes
```

#### 预期结果
✅ **100% 成功，0% 丢包！**

---

### 方法 B：演示问题排查过程（展示调试能力）

**适用场景**：展示完整的 **发现问题 → 诊断 → 解决** 过程

#### 步骤 1：运行有问题的版本
```bash
# 清理环境
sudo mn -c

# 运行问题版本
cd ~/桌面/lab/lab1
sudo python3 fat_tree_topo_4_bad.py
```

#### 步骤 2：演示问题现象
在 Mininet CLI 中执行：

```bash
# 测试连通性 - 会失败
pingall

# 诊断 1：查看交换机失败模式
sh ovs-vsctl get-fail-mode e00
# 输出：secure（问题根源 1）

# 诊断 2：查看流表
sh ovs-ofctl dump-flows e00
# 输出：有 NORMAL action，但仍不转发

# 诊断 3：测试同一交换机下的主机
h1 ping -c 3 h2
# 仍然失败！

# 诊断 4：查看主机状态
h1 ifconfig
# 注意：RX packets 和 dropped 数量异常巨大（数百万）
# 这说明存在广播风暴！
```

#### 步骤 3：分析并解决问题

**问题 1：Fail Mode 为 secure**

```bash
# 将所有交换机改为 standalone 模式
sh ovs-vsctl set-fail-mode e00 standalone
sh ovs-vsctl set-fail-mode e01 standalone
sh ovs-vsctl set-fail-mode e10 standalone
sh ovs-vsctl set-fail-mode e11 standalone
sh ovs-vsctl set-fail-mode e20 standalone
sh ovs-vsctl set-fail-mode e21 standalone
sh ovs-vsctl set-fail-mode e30 standalone
sh ovs-vsctl set-fail-mode e31 standalone
sh ovs-vsctl set-fail-mode a00 standalone
sh ovs-vsctl set-fail-mode a01 standalone
sh ovs-vsctl set-fail-mode a10 standalone
sh ovs-vsctl set-fail-mode a11 standalone
sh ovs-vsctl set-fail-mode a20 standalone
sh ovs-vsctl set-fail-mode a21 standalone
sh ovs-vsctl set-fail-mode a30 standalone
sh ovs-vsctl set-fail-mode a31 standalone
sh ovs-vsctl set-fail-mode c0 standalone
sh ovs-vsctl set-fail-mode c1 standalone
sh ovs-vsctl set-fail-mode c2 standalone
sh ovs-vsctl set-fail-mode c3 standalone

# 验证
sh ovs-vsctl get-fail-mode e00
# 输出：standalone
```

**问题 2：广播风暴（环路）**

```bash
# 启用 STP（生成树协议）
sh ovs-vsctl set Bridge e00 stp_enable=true
sh ovs-vsctl set Bridge e01 stp_enable=true
sh ovs-vsctl set Bridge e10 stp_enable=true
sh ovs-vsctl set Bridge e11 stp_enable=true
sh ovs-vsctl set Bridge e20 stp_enable=true
sh ovs-vsctl set Bridge e21 stp_enable=true
sh ovs-vsctl set Bridge e30 stp_enable=true
sh ovs-vsctl set Bridge e31 stp_enable=true
sh ovs-vsctl set Bridge a00 stp_enable=true
sh ovs-vsctl set Bridge a01 stp_enable=true
sh ovs-vsctl set Bridge a10 stp_enable=true
sh ovs-vsctl set Bridge a11 stp_enable=true
sh ovs-vsctl set Bridge a20 stp_enable=true
sh ovs-vsctl set Bridge a21 stp_enable=true
sh ovs-vsctl set Bridge a30 stp_enable=true
sh ovs-vsctl set Bridge a31 stp_enable=true
sh ovs-vsctl set Bridge c0 stp_enable=true
sh ovs-vsctl set Bridge c1 stp_enable=true
sh ovs-vsctl set Bridge c2 stp_enable=true
sh ovs-vsctl set Bridge c3 stp_enable=true

# 等待 STP 收敛（约 30 秒）
# 可以尝试多次 ping 查看进度
h1 ping -c 3 h2
```

#### 步骤 4：验证解决方案
```bash
# 测试同一交换机下的主机
h1 ping -c 3 h2
# ✅ 成功！

# 测试全网连通性
pingall
# ✅ 240/240 成功！
```

#### 步骤 5：对比自动化版本
```bash
# 退出
exit

# 清理
sudo mn -c

# 运行自动化版本
sudo python3 fat_tree_topo.py
# ✅ 直接成功，无需手动配置！
```

---

## 📊 数据收集与分析（用于实验报告）

### 1. 查看 MAC 地址学习表

#### 追踪 h1 → h16 的路径（跨 Pod 通信）

```bash
# h1 连接的边缘交换机（Pod0）
sh ovs-appctl fdb/show e00

# h1 所在 Pod 的聚合交换机
sh ovs-appctl fdb/show a00

# 核心交换机
sh ovs-appctl fdb/show c0

# h16 所在 Pod 的聚合交换机（Pod3）
sh ovs-appctl fdb/show a30

# h16 连接的边缘交换机（Pod3）
sh ovs-appctl fdb/show e30
```

**预期结果示例**：

```
e00 MAC 表：
- Port 1: h1 (00:00:00:00:00:01)
- Port 2: h2 (00:00:00:00:00:02)
- Port 3: h3, h4 (通过 a00)
- Port 4: h9-h16 (通过 a01 → 核心层)

a00 MAC 表：
- Port 1: h1, h2 (通过 e00)
- Port 2: h3, h4 (通过 e01)
- Port 4: h5-h16 (通过核心层)

c0 MAC 表：
- Port 1: h1-h4 (Pod0)
- Port 2: h5-h8 (Pod1)
- Port 3: h9-h12 (Pod2)
- Port 4: h13-h16 (Pod3)
```

### 2. 查看 STP 状态

```bash
# 查看边缘交换机 STP 状态
sh ovs-appctl stp/show e00

# 查看聚合交换机 STP 状态
sh ovs-appctl stp/show a00

# 查看核心交换机 STP 状态
sh ovs-appctl stp/show c0
```

**关键信息**：
- **Root Bridge**（根桥）：通常是最先启动的交换机（如 e00）
- **Root Port**（根端口）：指向根桥的最短路径端口
- **Designated Port**（指定端口）：负责转发的端口
- **Blocked Port**（阻塞端口）：被 STP 阻塞以防止环路

### 3. 测试跨 Pod 通信

```bash
# 测试 Pod0 → Pod3
h1 ping -c 5 h16

# 测试 Pod1 → Pod2
h5 ping -c 5 h9

# 查看延迟统计
h1 ping -c 10 h16
```

### 4. 查看交换机端口信息

```bash
# 查看端口配置
sh ovs-ofctl show e00

# 查看流表统计
sh ovs-ofctl dump-flows e00
```

---

## 📝 实验报告模板

### 一、实验环境

- **操作系统**：Ubuntu Linux (虚拟机)
- **工具**：Mininet 2.3.0, Open vSwitch 3.3.4
- **拓扑类型**：FAT TREE (k=4)

### 二、拓扑结构

- **主机数量**：16 台 (h1-h16)
- **交换机数量**：20 台
  - **边缘层**（Edge）：8 台 (e00, e01, e10, e11, e20, e21, e30, e31)
  - **聚合层**（Aggregation）：8 台 (a00, a01, a10, a11, a20, a21, a30, a31)
  - **核心层**（Core）：4 台 (c0, c1, c2, c3)
- **Pod 数量**：4 个（每个 Pod 包含 2 个边缘交换机 + 2 个聚合交换机）

**主机 IP 地址分配规则**：
```
10.<Pod+1>.<Edge+1>.<Host+1>

例如：
- h1: 10.1.1.1 (Pod0, Edge0, Host0)
- h16: 10.4.2.2 (Pod3, Edge1, Host1)
```

### 三、遇到的问题及解决方案

#### 问题 1：Fail Mode 导致数据包无法转发

**现象**：
- `pingall` 完全失败（0% 成功率）
- 即使同一交换机下的主机（h1 ↔ h2）也无法通信
- ARP 表显示所有条目为 `incomplete`

**原因分析**：
- OVS 交换机默认 `fail-mode` 为 `secure`
- 在 secure 模式下，**无控制器时交换机不转发任何数据包**
- 即使流表中有 `NORMAL` action，交换机仍拒绝转发

**诊断命令**：
```bash
sh ovs-vsctl get-fail-mode e00  # 返回：secure
sh ovs-ofctl dump-flows e00     # 显示有 NORMAL action
h1 ping -c 3 h2                 # 失败
```

**解决方案**：
将所有交换机的 fail-mode 改为 `standalone` 模式：
```bash
sh ovs-vsctl set-fail-mode <交换机名> standalone
```

在 standalone 模式下，交换机像传统二层交换机一样工作，进行 MAC 地址自学习和转发。

---

#### 问题 2：广播风暴（Broadcast Storm）

**现象**：
- 交换机处理了**数百万个数据包**（示例：59 秒内 4,399,521 个包）
- 主机接收队列溢出，**丢弃数百万个包**（示例：4,158,753 个丢包）
- CPU 使用率极高
- ARP 请求无法得到响应（incomplete）

**原因分析**：
FAT TREE 拓扑存在**多个环路**：
```
每个边缘交换机 ↔ 2 个聚合交换机（环路 1）
每个聚合交换机 ↔ 2 个核心交换机（环路 2）
核心交换机 ↔ 所有 Pod 的聚合交换机（环路 3）
```

广播包（如 ARP）在环路中无限循环，导致网络瘫痪。

**诊断命令**：
```bash
h1 ifconfig
# 观察：RX packets 和 dropped 数量异常巨大

sh ovs-ofctl dump-flows e00
# 观察：n_packets 数量在短时间内暴增
```

**解决方案**：
启用 **STP（Spanning Tree Protocol，生成树协议）**：
```bash
sh ovs-vsctl set Bridge <交换机名> stp_enable=true
```

STP 工作原理：
1. 选举一个**根桥**（Root Bridge）
2. 计算每个交换机到根桥的**最短路径**
3. **阻塞**冗余路径的端口，消除环路
4. 保留无环的生成树拓扑

**收敛时间**：约 **30 秒**

### 四、最终测试结果

```
*** Ping: testing ping reachability
h1 -> h2 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 
h2 -> h1 h3 h4 h5 h6 h7 h8 h9 h10 h11 h12 h13 h14 h15 h16 
...（所有主机互通）
*** Results: 0% dropped (240/240 received)
```

- ✅ **16 个主机完全互联互通**
- ✅ **0% 丢包率**（240/240 包成功）
- ✅ 跨 Pod 通信延迟：**0.05-2.5 ms**

### 五、数据包路径分析

以 **h1 (Pod0) → h16 (Pod3)** 为例：

**主机信息**：
- h1: MAC `00:00:00:00:00:01`, IP `10.1.1.1`
- h16: MAC `00:00:00:00:00:10`, IP `10.4.2.2`

**完整路径**（通过 MAC 地址表追踪）：
```
h1 (00:00:00:00:00:01)
  ↓ [e00-eth1]
e00 (边缘交换机, Pod0)
  ↓ [e00-eth4, Port 4 学到 h16]
a01 (聚合交换机, Pod0)
  ↓ [a01-eth3 或 a01-eth4]
c0/c1/c2/c3 (核心交换机之一)
  ↓ [c*-eth4, Port 4 连接 Pod3]
a30 或 a31 (聚合交换机, Pod3)
  ↓ [a30-eth2]
e31 (边缘交换机, Pod3)
  ↓ [e31-eth2]
h16 (00:00:00:00:00:10)
```

**路径跳数**：**5 跳**

这符合 FAT TREE 理论：不同 Pod 之间的最短路径为 5 跳。

### 六、MAC 地址学习分析

**边缘交换机（e00）**：
- 学习到**直连主机** MAC（h1, h2）
- 学习到**同 Pod 其他边缘交换机**的主机 MAC（h3, h4）
- 学习到**其他 Pod 主机** MAC（通过聚合层和核心层）

**聚合交换机（a00）**：
- 学习到**本 Pod 所有主机** MAC（h1-h4）
- 学习到**其他 Pod 主机** MAC（通过核心层）

**核心交换机（c0）**：
- 学习到**所有 16 个主机**的 MAC 地址
- 根据 MAC 地址对应的 Pod，从相应端口转发

### 七、STP（生成树）分析

**根桥（Root Bridge）**：
- 系统 ID：`06:92:56:a9:05:49`（通常是第一个启动的交换机 e00）
- 所有交换机以根桥为中心构建生成树

**关键交换机的 STP 状态**：

**a00（聚合交换机）**：
```
Root Port: a00-eth1 (连接 e00，到根桥的最短路径)
Root Path Cost: 2
所有端口状态: forwarding（转发）
```

**c0（核心交换机）**：
```
Root Port: c0-eth1 (连接 a00)
Root Path Cost: 4
所有端口状态: forwarding（转发）
```

**STP 阻塞的端口**：
从收集的数据看，e00 和 c0 的所有端口都在 `forwarding` 状态，说明 STP 在其他交换机上成功阻塞了冗余路径的端口，消除了环路。

### 八、结论

在**无控制器模式**下，FAT TREE 拓扑成功连通需要满足：

1. **Standalone 模式**：
   - 让 OVS 交换机像传统二层交换机工作
   - 支持 MAC 地址自学习
   - 支持广播、单播、组播转发

2. **STP 协议**：
   - 自动检测并消除网络环路
   - 阻塞冗余路径，保留生成树拓扑
   - 动态适应拓扑变化

3. **MAC 自学习**：
   - 交换机自动学习 MAC 地址和对应端口
   - 建立转发表（FDB - Forwarding Database）
   - 根据目的 MAC 地址转发数据包

通过正确配置 **standalone 模式 + STP**，实现了 **16 个主机的完全连通**，验证了 FAT TREE 拓扑的设计原理。

---

## 📸 实验报告截图建议

1. **拓扑启动信息**
   - 显示 20 个交换机、16 个主机的创建过程
   - 显示 standalone 和 STP 配置过程

2. **pingall 成功结果**
   - 完整的 h1-h16 连通性矩阵
   - `0% dropped (240/240 received)` 结果

3. **MAC 地址表**
   - e00, a00, c0 的 FDB 表
   - 展示 MAC 地址学习情况

4. **STP 状态**
   - 显示根桥信息
   - 显示端口角色（root/designated/blocked）和状态（forwarding/blocking）

5. **跨 Pod ping 测试**
   - h1 ping h16 的延迟统计
   - 展示 5 跳路径的 RTT

6. **问题排查过程**（可选）
   - fail-mode 为 secure 时的失败截图
   - 广播风暴时的流量统计
   - 逐步解决后的成功结果

---

## 🔧 调试技巧

### 使用 debug.py 进入纯净 CLI

如果需要手动测试，不想自动执行 pingall：

```bash
sudo python3 debug.py
```

这个脚本：
- ✅ 创建拓扑
- ❌ **不自动配置** standalone 和 STP
- ❌ **不自动执行** pingall
- ✅ 直接进入 Mininet CLI

适用于逐步手动配置和测试。

### 查看实时流量

在 Mininet CLI 外的终端：

```bash
# 查看某个交换机的流量统计
sudo watch -n 1 "ovs-ofctl dump-flows e00 | grep n_packets"

# 使用 tcpdump 抓包
sudo tcpdump -i e00-eth1 -c 10

# 使用 Wireshark（需要 GUI）
sudo wireshark &
# 然后选择接口，如 e00-eth1
```

### 重置环境

如果遇到问题需要完全重置：

```bash
# 停止 Mininet
sudo mn -c

# 清理 OVS 配置
sudo ovs-vsctl list-br | xargs -I {} sudo ovs-vsctl del-br {}

# 杀死所有相关进程
sudo killall -9 controller ovs-testcontroller python python3

# 重启 OVS 服务
sudo service openvswitch-switch restart
```

---

## 📚 参考资料

- **FAT TREE 论文**：*A Scalable, Commodity Data Center Network Architecture*
- **Mininet 官方文档**：http://mininet.org/
- **Open vSwitch 文档**：https://www.openvswitch.org/
- **STP 协议标准**：IEEE 802.1D

---

## ✅ 检查清单

实验完成前请确认：

- [ ] 所有 16 个主机互联互通（pingall 0% dropped）
- [ ] 收集了关键交换机的 MAC 地址表
- [ ] 记录了 STP 根桥和端口状态
- [ ] 测试了跨 Pod 通信（h1 → h16）
- [ ] 截取了必要的实验结果截图
- [ ] 理解了 standalone 模式和 STP 的作用
- [ ] 能够解释为什么 FAT TREE 需要 STP
- [ ] 完成了实验报告

---

**实验完成！祝展示顺利！** 🎉

