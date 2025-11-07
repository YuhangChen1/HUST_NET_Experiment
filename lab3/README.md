# Lab 3: SDN 链路选择与故障恢复实验 🌐

## 📚 实验概述

本实验基于 OpenFlow/OS-Ken 控制器与 Mininet 仿真环境，通过 LLDP（链路层发现协议）实现链路发现和时延测量，掌握 SDN 网络中的动态路径选择和故障容错机制。

### 🎯 实验目标

- ✅ **任务一**：基于最少跳数的路径选择（`least_hops.py`）
- ✅ **任务二**：基于最小时延的路径选择（`shortest_delay.py`）
- ✅ **任务三**：实现链路故障容忍与自动恢复

### 📖 实验收获

- 理解 LLDP 协议在 SDN 中的拓扑发现机制
- 掌握链路时延测量原理（LLDP + Echo）
- 学会使用 NetworkX 进行图算法计算
- 理解 OpenFlow 事件驱动编程模型
- 实现网络故障自动恢复机制

---

## 🚀 环境准备

### 1. 进入实验目录

```bash
cd ~/桌面/lab/lab3
```

### 2. 同步依赖

```bash
uv sync
source .venv/bin/activate
```

### 3. 添加执行权限

```bash
chmod +x topo.py
```

### 4. 网络拓扑说明

本实验使用 `topo.py` 定义的网络拓扑：

```
        h1---s1---s9---h9
             |     | \
        h2---s2    |  s8---h8
             | \   | /
             |  s4-s5-s6---h6
             | /   |   |
        h3---s3   h5  s7---h7
             |
            h4
```

**关键链路延迟**（用于任务二）：
- `s6 ↔ s7`: 10ms（最优路径）
- `s7 ↔ s8`: 12ms
- `s8 ↔ s9`: 13ms
- `s5 ↔ s9`: 100ms（高延迟链路）

---

## 📝 任务一：最少跳数路径选择

### 🎯 任务目标

理解 SDN 控制器如何通过 LLDP 获取网络拓扑，并使用 NetworkX 计算最少跳数路径。

### 🔧 核心概念

#### 1. 网络拓扑发现流程

```
步骤 1: LLDP 发现交换机间链路
  控制器 → S1 (发送 LLDP)
  S1 → S2 (转发 LLDP)
  S2 → 控制器 (PacketIn)
  控制器解析 → 记录 (S1, S2) 链路

步骤 2: 主机发现（沉默主机问题）
  主机首次通信 → ARP 广播
  控制器收到 PacketIn → 记录主机位置
  
步骤 3: 构建拓扑图
  使用 NetworkX Graph 存储拓扑
  节点: 主机 + 交换机
  边: 链路（带权重属性）
```

#### 2. NetworkX 最短路径计算

```python
import networkx as nx

# 创建拓扑图
topo_map = nx.Graph()

# 添加边（hop=1 表示跳数权重）
topo_map.add_edge(src, dst, hop=1, is_host=False)

# 计算最短路径（基于 hop 权重）
paths = list(nx.shortest_simple_paths(topo_map, src, dst, weight='hop'))
shortest_path = paths[0]  # 第一条路径即为最短路径
```

**参数说明**：
- `src`: 源节点（IP 地址）
- `dst`: 目标节点（IP 地址）
- `weight`: 权重属性名称（'hop' 或 'delay'）
- 返回值: 路径列表，按成本从小到大排序

### 🛠️ 实验步骤

#### 步骤 1：理解拓扑获取机制

阅读 `network_awareness.py` 中的 `_get_topology()` 方法：

```python
def _get_topology(self):
    while True:
        # 获取所有主机、交换机、链路
        hosts = get_all_host(self)
        switches = get_all_switch(self)
        links = get_all_link(self)
        
        # 添加主机到拓扑图
        for host in hosts:
            if host.ipv4:
                self.topo_map.add_edge(
                    host.ipv4[0], host.port.dpid, 
                    hop=1, delay=0, is_host=True
                )
        
        # 添加交换机链路到拓扑图
        for link in links:
            self.topo_map.add_edge(
                link.src.dpid, link.dst.dpid, 
                hop=1, is_host=False
            )
```

**关键数据结构**：
- `Host` 对象: 包含 `ipv4`, `port`, `mac` 等属性
- `Link` 对象: 包含 `src`, `dst` (PortData 对象)
- `Switch` 对象: 包含 `dp` (Datapath), `ports` 等属性

#### 步骤 2：解决 ARP 环路问题

在 `least_hops.py` 的 `handle_arp()` 方法中实现环路检测：

```python
def handle_arp(self, msg, in_port, dst, src, pkt, pkt_type):
    """
    使用 (dpid, src_mac, dst_mac) -> in_port 的方法处理 ARP 环路
    """
    datapath = msg.datapath
    dpid = datapath.id
    parser = datapath.ofproto_parser
    ofproto = datapath.ofproto
    
    # 构造唯一键
    key = (dpid, src, dst)
    
    # 检测环路
    if key in self.sw:
        if self.sw[key] != in_port:
            # 环路！丢弃包
            self.logger.info(
                "ARP loop detected: dpid=%s, src=%s, dst=%s, "
                "in_port=%s (previous=%s)",
                dpid, src, dst, in_port, self.sw[key]
            )
            return  # 丢弃包
    else:
        # 首次记录
        self.sw[key] = in_port
    
    # 洪泛 ARP
    actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
    out = parser.OFPPacketOut(
        datapath=datapath, 
        buffer_id=msg.buffer_id, 
        in_port=in_port, 
        actions=actions, 
        data=msg.data
    )
    datapath.send_msg(out)
```

#### 步骤 3：运行实验

**终端 1：启动拓扑**
```bash
sudo ./topo.py
```

**终端 2：启动控制器**
```bash
uv run osken-manager least_hops.py --observe-links
```

**Mininet CLI 中：**
```bash
mininet> h2 ping -c 10 h9
```

### 📊 预期结果

**控制器输出示例**：
```
path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> 1:s2:2 -> 1:s4:3 -> 1:s5:2 -> 3:s9:1 -> 10.0.0.9
```

**说明**：
- 路径: h2 → s2 → s4 → s5 → s9 → h9
- 总跳数: 4 跳
- 前几次 ping 可能显示 "host not find/no path"（沉默主机现象）

### ✅ 任务一验证清单

- [ ] 理解 LLDP 拓扑发现原理
- [ ] 能够解释 NetworkX `shortest_simple_paths` 的使用方法
- [ ] 成功实现 ARP 环路检测
- [ ] 控制器输出正确的路径信息
- [ ] h2 能够 ping 通 h9

---

## 🕐 任务二：最小时延路径选择

### 🎯 任务目标

通过 LLDP 和 Echo 消息测量链路时延，计算从 h2 到 h9 的最小时延路径，并用 Ping RTT 验证。

### 📖 时延测量原理

#### 链路时延计算公式

对于链路 `(S1, S2)`，单向时延计算为：

\[
\text{delay} = \max\left(\frac{T_{\text{lldp12}} + T_{\text{lldp21}} - T_{\text{echo1}} - T_{\text{echo2}}}{2}, 0\right)
\]

其中：
- **T<sub>lldp12</sub>**: 控制器 → S1 → S2 → 控制器的往返时间（绿线）
- **T<sub>lldp21</sub>**: 控制器 → S2 → S1 → 控制器的往返时间（蓝线）
- **T<sub>echo1</sub>**: 控制器 ↔ S1 的往返时间（红线）
- **T<sub>echo2</sub>**: 控制器 ↔ S2 的往返时间（黄线）

#### 时延测量示意图

```
Controller ←---T_echo1---→ S1 ←---链路---→ S2 ←---T_echo2---→ Controller
              (红线)                              (黄线)

LLDP 往返:
Controller → S1 → S2 → Controller  (T_lldp12, 绿线)
Controller → S2 → S1 → Controller  (T_lldp21, 蓝线)
```

**推导逻辑**：
```
T_lldp12 = T_echo1/2 + link_delay + T_echo2/2
T_lldp21 = T_echo2/2 + link_delay + T_echo1/2

相加：
T_lldp12 + T_lldp21 = T_echo1 + T_echo2 + 2 * link_delay

解出：
link_delay = (T_lldp12 + T_lldp21 - T_echo1 - T_echo2) / 2
```

### 🛠️ 实现步骤

#### 步骤 1：修改 OS-Ken 源文件支持 LLDP 时延测量

**1.1 修改 PortData 类**

编辑文件：`.venv/lib/python3.13/site-packages/os_ken/topology/switches.py`

```python
class PortData(object):
    def __init__(self, is_down, lldp_data):
        super(PortData, self).__init__()
        self.is_down = is_down
        self.lldp_data = lldp_data
        self.timestamp = None    # 新增：记录 LLDP 发送时间
        self.sent = 0
        self.delay = 0           # 新增：记录 T_lldp
```

**1.2 在 lldp_packet_in_handler 中计算 T<sub>lldp</sub>**

在同一文件中，找到 `lldp_packet_in_handler` 方法并修改：

```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def lldp_packet_in_handler(self, ev):
    # ========== 新增开始 ==========
    recv_timestamp = time.time()  # 记录接收时间
    # ========== 新增结束 ==========
    
    if not self.link_discovery:
        return
    
    msg = ev.msg
    try:
        src_dpid, src_port_no = LLDPPacket.lldp_parse(msg.data)
    except LLDPPacket.LLDPUnknownFormat:
        return
    
    # ========== 新增开始 ==========
    # 计算 LLDP 时延并保存到 port_data
    for port, port_data in self.ports.items():
        if src_dpid == port.dpid and src_port_no == port.port_no:
            send_timestamp = port_data.timestamp
            if send_timestamp:
                port_data.delay = recv_timestamp - send_timestamp
    # ========== 新增结束 ==========
    
    # ... 原有代码 ...
```

#### 步骤 2：在 NetworkAwareness 中添加数据结构

编辑 `network_awareness.py`：

```python
def __init__(self, *args, **kwargs):
    super(NetworkAwareness, self).__init__(*args, **kwargs)
    # ... 原有代码 ...
    
    # ========== 新增数据结构 ==========
    self.lldp_delay_table = {}    # (src_dpid, dst_dpid) -> T_lldp
    self.switches = {}             # switches 实例
    self.echo_RTT_table = {}       # dpid -> T_echo
    self.echo_send_timestamp = {}  # dpid -> send_time
    self.link_delay_table = {}     # (dpid1, dpid2) -> delay
```

#### 步骤 3：实现 LLDP 时延获取

在 `network_awareness.py` 中添加 `packet_in_handler`：

```python
from os_ken.base.app_manager import lookup_service_brick
from os_ken.topology.switches import LLDPPacket

@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
    """处理 LLDP 消息，获取 LLDP 时延"""
    msg = ev.msg
    dpid = msg.datapath.id
    
    try:
        src_dpid, src_port_no = LLDPPacket.lldp_parse(msg.data)
        
        # 获取 switches 实例（只需获取一次）
        if not self.switches:
            self.switches = lookup_service_brick('switches')
        
        # 从 switches 中获取 LLDP 时延
        for port in self.switches.ports.keys():
            if src_dpid == port.dpid and src_port_no == port.port_no:
                # 保存 T_lldp
                self.lldp_delay_table[(src_dpid, dpid)] = \
                    self.switches.ports[port].delay
                break
    except:
        return
```

#### 步骤 4：周期发送 Echo 请求

**4.1 实现 send_echo_request**

```python
def send_echo_request(self, switch):
    """向交换机发送 Echo 请求"""
    datapath = switch.dp
    parser = datapath.ofproto_parser
    dpid = datapath.id
    
    # 记录发送时间
    send_time = time.time()
    self.echo_send_timestamp[dpid] = send_time
    
    # 构造 Echo 请求（data 必须是 bytes 类型）
    data = str(send_time).encode('utf-8')
    echo_req = parser.OFPEchoRequest(datapath, data=data)
    
    # 发送
    datapath.send_msg(echo_req)
```

**4.2 实现 handle_echo_reply**

```python
@set_ev_cls(ofp_event.EventOFPEchoReply, MAIN_DISPATCHER)
def handle_echo_reply(self, ev):
    """处理 Echo 回复，计算 T_echo"""
    try:
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        
        # 记录接收时间
        recv_time = time.time()
        
        # 获取发送时间（可选：从 data 中解码验证）
        send_time = self.echo_send_timestamp.get(dpid)
        if send_time:
            # 计算 Echo RTT
            self.echo_RTT_table[dpid] = recv_time - send_time
    except Exception as e:
        self.logger.warning(f"Failed to handle echo reply: {e}")
```

**4.3 周期性发送 Echo**

```python
def examine_echo_RTT(self):
    """周期性测量 Echo RTT"""
    while True:
        # 获取所有交换机
        switches = get_all_switch(self)
        
        # 向每个交换机发送 Echo
        for switch in switches:
            self.send_echo_request(switch)
        
        # 睡眠（使用 hub.sleep 减少影响）
        hub.sleep(SEND_ECHO_REQUEST_INTERVAL)

# 在 __init__ 中启动线程
def __init__(self, *args, **kwargs):
    # ... 原有代码 ...
    
    # 启动 Echo 测量线程
    self.echo_thread = hub.spawn(self.examine_echo_RTT)
```

#### 步骤 5：计算链路时延

**5.1 实现 calculate_link_delay**

```python
def calculate_link_delay(self, src_dpid, dst_dpid):
    """
    计算链路单向时延
    公式: delay = max((T_lldp12 + T_lldp21 - T_echo1 - T_echo2) / 2, 0)
    """
    try:
        # 获取 LLDP 往返时延
        lldp_12 = self.lldp_delay_table.get((src_dpid, dst_dpid), 0)
        lldp_21 = self.lldp_delay_table.get((dst_dpid, src_dpid), 0)
        
        # 获取 Echo RTT
        echo_1 = self.echo_RTT_table.get(src_dpid, 0)
        echo_2 = self.echo_RTT_table.get(dst_dpid, 0)
        
        # 计算链路时延
        delay = (lldp_12 + lldp_21 - echo_1 - echo_2) / 2
        
        # 确保非负
        return max(delay, 0)
    except KeyError:
        # 链路发现和延迟计算是异步的，可能出现键不存在的情况
        return 0
```

**5.2 在 _get_topology 中更新拓扑**

修改 `_get_topology()` 方法中添加边的部分：

```python
for link in links:
    # ... 原有代码 ...
    
    # ========== 新增：计算链路时延 ==========
    delay = self.calculate_link_delay(link.src.dpid, link.dst.dpid)
    
    # 输出链路时延信息
    self.logger.info(
        "Link: %s -> %s, delay: %.5fms",
        link.src.dpid, link.dst.dpid, delay * 1000
    )
    
    # 添加边到拓扑图（包含 delay 属性）
    self.topo_map.add_edge(
        link.src.dpid, link.dst.dpid, 
        hop=1, 
        delay=delay,  # 新增 delay 属性
        is_host=False
    )
```

#### 步骤 6：实现最小时延路径控制器

**6.1 修改 shortest_delay.py**

```python
class ShortestDelay(app_manager.OSKenApp):
    def __init__(self, *args, **kwargs):
        super(ShortestDelay, self).__init__(*args, **kwargs)
        self.network_awareness = kwargs['network_awareness']
        self.weight = 'delay'  # ⚠️ 改为 'delay'
        self.mac_to_port = {}
        self.sw = {}
        self.path = None
```

**6.2 在 handle_ipv4 中计算路径时延**

```python
def handle_ipv4(self, msg, src_ip, dst_ip, pkt_type):
    parser = msg.datapath.ofproto_parser
    
    # 计算最短路径（基于 delay）
    dpid_path = self.network_awareness.shortest_path(
        src_ip, dst_ip, weight=self.weight
    )
    if not dpid_path:
        return
    
    self.path = dpid_path
    
    # 获取端口路径
    port_path = []
    for i in range(1, len(dpid_path) - 1):
        in_port = self.network_awareness.link_info[(dpid_path[i], dpid_path[i - 1])]
        out_port = self.network_awareness.link_info[(dpid_path[i], dpid_path[i + 1])]
        port_path.append((in_port, dpid_path[i], out_port))
    
    self.show_path(src_ip, dst_ip, port_path)
    
    # ========== 新增：计算路径时延 ==========
    # 构建链路时延字典
    link_delay_dict = {}
    path_delay = 0.0
    
    for i in range(1, len(dpid_path) - 1):
        src = dpid_path[i]
        dst = dpid_path[i + 1]
        
        # 从拓扑图中获取时延
        if self.network_awareness.topo_map.has_edge(src, dst):
            delay = self.network_awareness.topo_map[src][dst].get('delay', 0)
            link_delay_dict[f"s{src}->s{dst}"] = delay * 1000  # 转换为 ms
            path_delay += delay
    
    # 计算 Path RTT（往返时间 = 2 * 单向时延）
    path_RTT = path_delay * 2
    
    # 输出结果
    self.logger.info('link delay dict: %s', link_delay_dict)
    self.logger.info("path delay = %.5fms", path_delay * 1000)
    self.logger.info("path RTT = %.5fms", path_RTT * 1000)
    
    # ... 下发流表 ...
```

**6.3 实现 ARP 环路检测**

与任务一相同，在 `handle_arp()` 中实现环路检测逻辑。

### 🚀 运行实验

**终端 1：启动拓扑**
```bash
sudo ./topo.py
```

**终端 2：启动控制器**
```bash
uv run osken-manager shortest_delay.py --observe-links
```

**Mininet CLI 中：**
```bash
mininet> h2 ping -c 10 h9
```

### 📊 预期结果

**控制器输出示例**：
```
Link: 2 -> 3, delay: 32.00000ms
Link: 2 -> 4, delay: 80.00000ms
Link: 6 -> 7, delay: 20.00000ms
Link: 8 -> 9, delay: 26.00000ms

path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> 1:s2:3 -> 2:s4:2 -> 1:s5:3 -> 2:s6:1 -> 1:s7:2 -> 1:s8:2 -> 3:s9:1 -> 10.0.0.9

link delay dict: {'s2->s4': 80.0, 's4->s5': 110.0, 's5->s6': 30.0, 's6->s7': 20.0, 's7->s8': 24.0, 's8->s9': 26.0}
path delay = 290.00000ms
path RTT = 580.00000ms
```

**Ping 输出对比**：
```
64 bytes from 10.0.0.9: icmp_seq=1 ttl=64 time=270 ms  ✅ 接近 path delay
64 bytes from 10.0.0.9: icmp_seq=2 ttl=64 time=268 ms
```

**说明**：
- Ping RTT ≈ path delay * 2（往返）
- 实际 RTT 略小于计算值（流表缓存后无需经过控制器）

### ✅ 任务二验证清单

- [ ] 成功修改 OS-Ken 源文件
- [ ] 实现 LLDP 时延获取
- [ ] 实现 Echo RTT 测量
- [ ] 正确计算链路时延
- [ ] 输出路径时延和 Ping RTT
- [ ] Ping RTT 与计算值接近

---

## 🔧 任务三：容忍链路故障

### 🎯 任务目标

在链路故障或恢复时，控制器能自动检测并重新选择最优路径，保证通信不中断。

### 📖 故障恢复原理

#### 链路状态变化事件

当链路状态发生变化时，OpenFlow 交换机会触发 `EventOFPPortStatus` 事件：

```python
@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
def port_status_handler(self, ev):
    msg = ev.msg
    reason = msg.reason
    
    # reason 类型：
    # - OFPPR_ADD: 端口新增
    # - OFPPR_MODIFY: 端口修改（link up/down）
    # - OFPPR_DELETE: 端口删除
```

#### 故障恢复流程

```
步骤 1: 链路故障 (link s6 s7 down)
  → 触发 EventOFPPortStatus
  → reason = OFPPR_MODIFY

步骤 2: 清理旧数据
  → 清空拓扑图 (topo_map.clear())
  → 删除所有流表
  → 清空 sw、mac_to_port

步骤 3: 重新发现拓扑
  → LLDP 自动重新发现
  → 构建新的拓扑图

步骤 4: 自动路径切换
  → 交换机无流表 → PacketIn
  → 控制器重新计算最优路径
  → 下发新流表
```

### 🛠️ 实现步骤

#### 步骤 1：实现端口状态监听

在 `shortest_delay.py` 中添加 `port_status_handler`：

```python
from os_ken.topology.api import get_all_switch

@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
def port_status_handler(self, ev):
    """处理端口状态变化事件"""
    msg = ev.msg
    datapath = msg.datapath
    ofproto = datapath.ofproto
    
    if msg.reason in [ofproto.OFPPR_ADD, ofproto.OFPPR_MODIFY]:
        # 端口新增或修改（link up 和 link down 都属于修改）
        datapath.ports[msg.desc.port_no] = msg.desc
        
        self.logger.info(
            "Port status changed on switch %s, port %s",
            datapath.id, msg.desc.port_no
        )
        
        # ========== 清理数据 ==========
        # 1. 清空拓扑图
        self.network_awareness.topo_map.clear()
        self.logger.info("Topology map cleared")
        
        # 2. 删除所有流表
        self.delete_all_flow()
        self.logger.info("All flow entries deleted")
        
        # 3. 清空 sw（ARP 环路检测表）
        self.sw.clear()
        
        # 4. 清空 mac_to_port（自学习表）
        self.mac_to_port.clear()
        
    elif msg.reason == ofproto.OFPPR_DELETE:
        datapath.ports.pop(msg.desc.port_no, None)
    else:
        return
```

#### 步骤 2：实现流表删除

**2.1 删除单个交换机端口的流表**

```python
def delete_flow(self, datapath, port_no):
    """删除指定端口相关的流表"""
    ofproto = datapath.ofproto
    parser = datapath.ofproto_parser
    
    try:
        # ========== 删除 in_port 匹配的流表 ==========
        match_in = parser.OFPMatch(in_port=port_no)
        mod_in = parser.OFPFlowMod(
            datapath=datapath,
            command=ofproto.OFPFC_DELETE,  # 删除命令
            out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY,
            match=match_in
        )
        datapath.send_msg(mod_in)
        
        # ========== 删除 out_port 匹配的流表 ==========
        # 注意：需要指定 out_port 参数
        match_out = parser.OFPMatch()
        mod_out = parser.OFPFlowMod(
            datapath=datapath,
            command=ofproto.OFPFC_DELETE,
            out_port=port_no,  # 指定输出端口
            out_group=ofproto.OFPG_ANY,
            match=match_out
        )
        datapath.send_msg(mod_out)
        
        self.logger.info(
            "Deleted flow entries for port %s on switch %s",
            port_no, datapath.id
        )
        
    except Exception as e:
        self.logger.error(
            "Failed to delete flow entries for port %s on switch %s: %s",
            port_no, datapath.id, str(e)
        )
```

**2.2 删除所有交换机的流表**

```python
def delete_all_flow(self):
    """删除所有交换机的所有流表"""
    switches = get_all_switch(self.network_awareness)
    
    for switch in switches:
        datapath = switch.dp
        
        # 遍历交换机的所有端口
        for port_no in switch.ports:
            # 跳过本地端口和控制器端口
            if port_no.port_no == datapath.ofproto.OFPP_LOCAL:
                continue
            
            self.delete_flow(datapath, port_no.port_no)
```

**简化版本（删除所有流表）**：

```python
def delete_all_flow(self):
    """删除所有交换机的所有流表（简化版）"""
    switches = get_all_switch(self.network_awareness)
    
    for switch in switches:
        datapath = switch.dp
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # 构造空匹配（匹配所有流表）
        match = parser.OFPMatch()
        
        # 发送删除命令
        mod = parser.OFPFlowMod(
            datapath=datapath,
            command=ofproto.OFPFC_DELETE,
            out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY,
            match=match
        )
        datapath.send_msg(mod)
        
        self.logger.info("Deleted all flows on switch %s", datapath.id)
```

### 🚀 运行实验

**终端 1：启动拓扑**
```bash
sudo ./topo.py
```

**终端 2：启动控制器**
```bash
uv run osken-manager shortest_delay.py --observe-links
```

**Mininet CLI 中：测试故障恢复**

**步骤 1：初始状态**
```bash
mininet> h2 ping h9
# 观察路径和 RTT（约 270ms）
```

**步骤 2：模拟链路故障**
```bash
mininet> link s6 s7 down
# 稍等片刻，让控制器重新发现拓扑
# ping 会自动恢复，但 RTT 增加（约 370ms）
```

**步骤 3：恢复链路**
```bash
mininet> link s6 s7 up
# 稍等片刻
# ping RTT 恢复到 270ms
```

### 📊 预期结果

**初始状态**：
```
path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> ... -> s6 -> s7 -> s8 -> s9 -> 10.0.0.9
path delay = 270.00000ms
```

**链路故障后（s6-s7 down）**：
```
Port status changed on switch 6, port 2
Topology map cleared
All flow entries deleted

path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> ... -> s5 -> s9 -> 10.0.0.9  (绕过 s6-s7)
path delay = 370.00000ms  ⚠️ 延迟增加
```

**链路恢复后（s6-s7 up）**：
```
Port status changed on switch 6, port 2
Topology map cleared
All flow entries deleted

path: 10.0.0.2 -> 10.0.0.9
10.0.0.2 -> ... -> s6 -> s7 -> s8 -> s9 -> 10.0.0.9  ✅ 恢复最优路径
path delay = 270.00000ms
```

### ✅ 任务三验证清单

- [ ] 成功捕获 `EventOFPPortStatus` 事件
- [ ] 链路故障时自动切换路径
- [ ] 链路恢复时自动恢复最优路径
- [ ] ping 通信不中断
- [ ] 能够解释为什么需要清空拓扑图和流表

#### 5.5 实现要点补充（2025 更新）

- **端口事件去重**：`shortest_delay.py` 中为 `(dpid, port)` 记录最后一次处理时间，确保链路抖动时不会重复清空拓扑，避免 PacketIn 一直缺失。
- **重新安装默认流表**：删除旧流表后立即写入优先级 0 的 `controller` 转发表，保证新包仍会上送控制器触发重新选路。
- **等待拓扑重建**：链路恢复后需等待 LLDP / Echo 周期（约 5~10s），确认日志出现新的 `Link: X -> Y` 再进行连通性验证。

---

## 📝 实验报告要求

### 📊 报告结构建议

#### 一、实验目的（1 段）
- 理解 SDN 链路发现机制（LLDP）
- 掌握链路时延测量方法
- 学习网络故障自动恢复

#### 二、实验环境（表格）
```
操作系统：Ubuntu Linux (虚拟机)
工具软件：Mininet, OS-Ken, NetworkX
Python 版本：3.13
OpenFlow 版本：1.3
```

#### 三、任务一：最少跳数路径（2-3 页）

**3.1 NetworkX 最短路径算法说明**
- `networkx.shortest_simple_paths` 的使用方法
- 参数说明（src, dst, weight）
- 返回值解释

**3.2 ARP 环路检测实现**
- 使用 `(dpid, src_mac, dst_mac) -> in_port` 映射表
- 环路判断逻辑
- 关键代码

**3.3 实验结果**
- 截图：控制器输出的路径信息
- 截图：ping 成功（h2 → h9）
- 分析：路径选择是否最优

#### 四、任务二：最小时延路径（4-5 页）

**4.1 LLDP 时延测量原理**（重点！）
- LLDP 往返时间测量
- Echo RTT 测量
- 链路单向时延计算公式推导

**4.2 代码实现**
- 修改 OS-Ken 源文件（PortData 类）
- LLDP 时延获取（packet_in_handler）
- Echo 周期发送（send_echo_request）
- Echo 回复处理（handle_echo_reply）
- 链路时延计算（calculate_link_delay）

**4.3 实验结果**
- 截图：控制器输出的链路时延
- 截图：路径时延和 link delay dict
- 截图：Ping RTT 结果
- 对比分析：计算时延 vs 实际 RTT

**4.4 遇到的问题与解决**
- 问题 1：时延出现负值
  - 原因：异步计算，数据未就绪
  - 解决：使用 `max(delay, 0)` 和 `dict.get(key, default)`
- 问题 2：第一次 ping 显示 "host not find"
  - 原因：沉默主机现象
  - 解决：主机主动通信后自动发现

#### 五、任务三：链路故障容忍（3-4 页）

**5.1 故障检测机制**
- `EventOFPPortStatus` 事件处理
- 端口状态变化类型（ADD, MODIFY, DELETE）

**5.2 故障恢复流程**
- 清空拓扑图
- 删除流表
- 清空 sw、mac_to_port
- 自动路径重选

**5.3 实验结果**
- 截图：初始状态（s6-s7 链路正常）
- 截图：故障状态（s6-s7 down，路径切换）
- 截图：恢复状态（s6-s7 up，恢复最优路径）
- Mininet 控制台输出
- 控制器日志输出

**5.4 思考与分析**（重点！）

**问题：为什么需要清空拓扑图、sw，而不需要清空 lldp_delay_table？**

**答案**：

1. **需要清空拓扑图（topo_map）**：
   - 拓扑结构发生了变化（链路断开/恢复）
   - 旧的拓扑图包含已失效的边
   - 如果不清空，会计算出错误的路径（经过已断开的链路）
   - LLDP 会自动重新发现新的拓扑

2. **需要清空流表**：
   - 旧流表指向的路径可能已失效
   - 如果不删除，数据包会继续沿旧路径转发 → 丢包
   - 删除后，PacketIn 触发控制器重新计算路径

3. **需要清空 sw 和 mac_to_port**：
   - sw: ARP 环路检测表，旧的记录可能导致误判
   - mac_to_port: 自学习表，主机位置可能未变，但清空更安全

4. **不需要清空 lldp_delay_table、echo_RTT_table**：
   - 这些是**测量数据**，不是**拓扑结构**
   - 链路时延是链路的物理属性，不会因为端口状态变化而失效
   - 保留这些数据可以加快恢复速度
   - LLDP 和 Echo 会持续测量，自动更新数据

**对比表**：

| 数据结构 | 是否清空 | 原因 |
|---------|---------|------|
| `topo_map` (拓扑图) | ✅ 清空 | 拓扑结构变化，旧边失效 |
| 流表 (Flow Table) | ✅ 删除 | 旧路径失效，避免丢包 |
| `sw` (ARP 检测表) | ✅ 清空 | 避免误判环路 |
| `mac_to_port` | ✅ 清空 | 更安全（主机位置可能变化）|
| `lldp_delay_table` | ❌ 保留 | 测量数据，持续更新 |
| `echo_RTT_table` | ❌ 保留 | 测量数据，持续更新 |
| `link_delay_table` | ❌ 保留 | 自动重新计算 |

#### 六、实验总结（1-2 段）
- 实验收获
- 对 SDN 动态路由的理解
- 故障恢复机制的优缺点
- 与传统网络的对比

#### 七、思考题（可选）

**问题 1**：如果网络中有多条相同时延的路径，控制器会如何选择？

**问题 2**：LLDP 无法发现主机，如何解决沉默主机问题？

**问题 3**：如果交换机与控制器之间的连接断开，网络会发生什么？

---

### 📸 必需的截图清单

#### 任务一（3 张）
1. ✅ 控制器输出（路径信息）
2. ✅ ping 成功截图（h2 → h9）
3. ✅ Wireshark 抓包（可选，验证路径）

#### 任务二（6 张）
1. ✅ 控制器输出（链路时延）
2. ✅ 控制器输出（link delay dict）
3. ✅ 控制器输出（path delay 和 path RTT）
4. ✅ Ping 输出（RTT 对比）
5. ✅ 代码截图（calculate_link_delay 实现）
6. ✅ 代码截图（handle_echo_reply 实现）

#### 任务三（6 张）
1. ✅ 初始状态：控制器输出（路径和延迟）
2. ✅ 初始状态：Ping 输出（RTT ≈ 270ms）
3. ✅ 故障状态：Mininet 执行 `link s6 s7 down`
4. ✅ 故障状态：控制器输出（新路径，延迟增加）
5. ✅ 恢复状态：Mininet 执行 `link s6 s7 up`
6. ✅ 恢复状态：控制器输出（恢复最优路径）

---

### 📋 实验数据记录模板

#### 任务一数据记录
```
最少跳数路径（h2 → h9）：
路径：10.0.0.2 → s__ → s__ → s__ → s__ → 10.0.0.9
跳数：__ 跳
Ping RTT：平均 __ms
```

#### 任务二数据记录
```
链路时延测量：
- s2 → s4: __ms
- s4 → s5: __ms
- s5 → s6: __ms
- s6 → s7: __ms
- s7 → s8: __ms
- s8 → s9: __ms

最小时延路径（h2 → h9）：
路径：10.0.0.2 → s__ → s__ → ... → 10.0.0.9
计算 path delay：__ms
计算 path RTT：__ms
实际 Ping RTT：__ms
误差：__(%)
```

#### 任务三数据记录
```
初始状态（s6-s7 正常）：
路径：__
延迟：__ms
Ping RTT：__ms

故障状态（s6-s7 down）：
路径：__（绕过 s6-s7）
延迟：__ms（增加）
Ping RTT：__ms

恢复状态（s6-s7 up）：
路径：__（恢复原路径）
延迟：__ms（恢复）
Ping RTT：__ms
```

---

## 🛠️ 常用命令速查

### Mininet CLI 命令

```bash
# 测试连通性
mininet> h2 ping -c 10 h9

# 查看网络拓扑
mininet> net

# 查看所有节点
mininet> nodes

# 查看链路
mininet> links

# 模拟链路故障
mininet> link s6 s7 down

# 恢复链路
mininet> link s6 s7 up

# 退出
mininet> exit
```

### 控制器命令

```bash
# 启动 least_hops 控制器
uv run osken-manager least_hops.py --observe-links

# 启动 shortest_delay 控制器
uv run osken-manager shortest_delay.py --observe-links

# 启动 show_topo（查看拓扑）
uv run osken-manager show_topo.py --observe-links
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

## 🐛 常见问题

### 1. 时延出现负值

**现象**：
```
Link: 2 -> 3, delay: -5.23456ms
```

**原因**：
- LLDP 时延和 Echo RTT 测量是异步的
- 某些数据可能尚未测量完成

**解决**：
```python
def calculate_link_delay(self, src_dpid, dst_dpid):
    # 使用 get() 提供默认值
    lldp_12 = self.lldp_delay_table.get((src_dpid, dst_dpid), 0)
    # ...
    delay = (lldp_12 + lldp_21 - echo_1 - echo_2) / 2
    return max(delay, 0)  # 确保非负
```

### 2. "host not find/no path"

**现象**：
```
host not find/no path
host not find/no path
path: 10.0.0.2 -> 10.0.0.9  (第3次才成功)
```

**原因**：
- 沉默主机现象：主机未主动通信前，控制器无法感知
- LLDP 只能发现交换机，不能发现主机

**解决**：
- 这是正常现象，前几次 ping 会自动触发主机发现
- 可以通过 `pingall` 预先发现所有主机

### 3. 修改 OS-Ken 源文件后无效

**现象**：
- 修改了 `.venv/lib/.../switches.py`
- 但是时延仍然为 0

**原因**：
- Python 可能使用了缓存的 `.pyc` 文件

**解决**：
```bash
# 删除缓存
find .venv -name "*.pyc" -delete
find .venv -name "__pycache__" -type d -exec rm -rf {} +

# 或者重新安装依赖
uv sync --reinstall
```

### 4. 链路故障后 ping 中断

**现象**：
```
64 bytes from 10.0.0.9: icmp_seq=1 ttl=64 time=270 ms
(执行 link s6 s7 down)
Request timeout for icmp_seq 2
Request timeout for icmp_seq 3
64 bytes from 10.0.0.9: icmp_seq=4 ttl=64 time=370 ms
```

**原因**：
- 链路断开后，拓扑重新发现需要时间
- 正常现象，几秒后会自动恢复

**解决**：
- 这是预期行为，说明故障检测正常工作
- 可以调整 `GET_TOPOLOGY_INTERVAL` 减少恢复时间

### 5. Echo 请求发送失败

**错误**：
```
TypeError: data argument must be bytes
```

**原因**：
- `OFPEchoRequest` 的 `data` 参数必须是 `bytes` 类型

**解决**：
```python
# 错误写法
data = str(time.time())

# 正确写法
data = str(time.time()).encode('utf-8')
```

---

## 💡 实验技巧

### 1. 使用日志调试

在代码中添加详细的日志输出：

```python
self.logger.info("LLDP delay: (%s, %s) -> %.5fms", 
                 src_dpid, dst_dpid, delay * 1000)
self.logger.debug("Echo RTT table: %s", self.echo_RTT_table)
```

### 2. 使用 Git 版本管理

```bash
# 提交修改前的代码
git add network_awareness.py
git commit -m "Before adding delay measurement"

# 实验后对比差异
git diff HEAD~1
```

### 3. 使用 VSCode 搜索功能

- `Ctrl + F`: 文件内搜索
- `Ctrl + Shift + F`: 全局搜索
- `Ctrl + Click`: 跳转到定义

### 4. 查看 NetworkX 图结构

在代码中添加调试输出：

```python
def show_topo_detail(self):
    """显示拓扑图详细信息"""
    for src, dst, data in self.topo_map.edges(data=True):
        self.logger.info("Edge: %s -> %s, data: %s", src, dst, data)
```

---

## 📚 参考资料

### 官方文档

- [OS-Ken 官方文档](https://docs.openstack.org/os-ken/latest/)
- [Mininet 官方文档](http://mininet.org/)
- [NetworkX 文档](https://networkx.org/documentation/stable/)
- [OpenFlow 1.3 规范](https://www.opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.3.0.pdf)

### 关键 API 文档

- [OFPEchoRequest](https://osrg.github.io/ryu-book/en/html/openflow_protocol.html)
- [EventOFPPortStatus](https://osrg.github.io/ryu-book/en/html/openflow_protocol.html#port-status-message)
- [OFPFlowMod](https://osrg.github.io/ryu-book/en/html/openflow_protocol.html#modify-state-messages)
- [networkx.shortest_simple_paths](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.shortest_simple_paths.html)

### 相关论文

- [LLDP: Link Layer Discovery Protocol](https://en.wikipedia.org/wiki/Link_Layer_Discovery_Protocol)
- [SDN 架构与 OpenFlow](https://www.sdnlab.com/)

---

## ✅ 实验完成检查清单

### 任务一
- [ ] 理解 LLDP 拓扑发现原理
- [ ] 理解 NetworkX 最短路径算法
- [ ] 实现 ARP 环路检测
- [ ] 控制器输出正确路径
- [ ] ping 测试成功

### 任务二
- [ ] 修改 OS-Ken 源文件（PortData, lldp_packet_in_handler）
- [ ] 实现 LLDP 时延获取（packet_in_handler）
- [ ] 实现 Echo 周期发送（send_echo_request, examine_echo_RTT）
- [ ] 实现 Echo 回复处理（handle_echo_reply）
- [ ] 实现链路时延计算（calculate_link_delay）
- [ ] 修改拓扑图添加 delay 属性
- [ ] 修改 weight 为 'delay'
- [ ] 输出 path delay 和 path RTT
- [ ] Ping RTT 与计算值接近

### 任务三
- [ ] 实现端口状态监听（port_status_handler）
- [ ] 实现流表删除（delete_flow, delete_all_flow）
- [ ] 清空拓扑图、sw、mac_to_port
- [ ] 测试链路故障（link down）
- [ ] 测试链路恢复（link up）
- [ ] 能够解释为什么需要清空某些数据结构

---

**实验完成！祝你顺利通过！** 🎉

如有问题，请参考常见问题部分或查阅官方文档。

