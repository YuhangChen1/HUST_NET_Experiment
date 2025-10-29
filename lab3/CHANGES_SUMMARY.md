# Lab 3 代码修改总结 📝

## ✅ 已完成的修改

本文档总结了 Lab 3 中所有代码文件的修改内容。

---

## 📄 修改的文件列表

### 1. `least_hops.py` - 任务一实现

**修改内容：**
- ✅ 实现 `handle_arp()` 函数
- ✅ ARP 环路检测逻辑（使用 `(dpid, src_mac, dst_mac) -> in_port` 映射）
- ✅ ARP 包洪泛处理

**关键代码：**
```python
def handle_arp(self, msg, in_port, dst, src, pkt, pkt_type):
    """Handle ARP packets and prevent ARP loop"""
    # 环路检测
    key = (dpid, src, dst)
    if key in self.sw and self.sw[key] != in_port:
        # 丢弃环路包
        return
    self.sw[key] = in_port
    # 洪泛 ARP
```

**验证方法：**
```bash
uv run osken-manager least_hops.py --observe-links
# 在 Mininet 中：h2 ping h9
```

---

### 2. `network_awareness.py` - 任务二核心实现

**修改内容：**

#### 2.1 添加数据结构（`__init__` 方法）
```python
self.lldp_delay_table = {}    # (src_dpid, dst_dpid) -> T_lldp
self.switches = {}             # switches app instance
self.echo_RTT_table = {}       # dpid -> T_echo
self.echo_send_timestamp = {}  # dpid -> send_time
self.link_delay_table = {}     # (dpid1, dpid2) -> delay
self.echo_thread = hub.spawn(self.examine_echo_RTT)
```

#### 2.2 添加 LLDP 时延获取（新增方法）
```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def packet_in_handler(self, ev):
    """Handle LLDP packets to get LLDP delay"""
    # 解析 LLDP 包
    # 从 switches 实例获取 T_lldp
    # 保存到 lldp_delay_table
```

#### 2.3 添加 Echo 周期发送（新增方法）
```python
def send_echo_request(self, switch):
    """Send Echo request to a switch"""
    # 记录发送时间
    # 构造 Echo 请求（data 必须是 bytes）
    # 发送

def examine_echo_RTT(self):
    """Periodically measure Echo RTT"""
    # 周期性向每个交换机发送 Echo
```

#### 2.4 添加 Echo 回复处理（新增方法）
```python
@set_ev_cls(ofp_event.EventOFPEchoReply, MAIN_DISPATCHER)
def handle_echo_reply(self, ev):
    """Handle Echo reply and calculate T_echo"""
    # 计算 Echo RTT
    # 保存到 echo_RTT_table
```

#### 2.5 添加链路时延计算（新增方法）
```python
def calculate_link_delay(self, src_dpid, dst_dpid):
    """Calculate link delay"""
    # 公式：delay = max((T_lldp12 + T_lldp21 - T_echo1 - T_echo2) / 2, 0)
    # 返回非负时延
```

#### 2.6 修改拓扑更新逻辑（`_get_topology` 方法）
```python
# 计算链路时延
delay = self.calculate_link_delay(link.src.dpid, link.dst.dpid)

# 存储到 link_delay_table
self.link_delay_table[(link.src.dpid, link.dst.dpid)] = delay

# 输出链路时延
self.logger.info("Link: %s -> %s, delay: %.5fms", ...)

# 添加边到拓扑图（包含 delay 属性）
self.topo_map.add_edge(..., delay=delay, ...)
```

**验证方法：**
```bash
# 查看控制器输出是否有链路时延信息
# Link: 2 -> 3, delay: 32.00000ms
```

---

### 3. `shortest_delay.py` - 任务二和任务三实现

**修改内容：**

#### 3.1 修改导入
```python
from os_ken.topology.api import get_all_switch  # 新增
```

#### 3.2 修改权重（`__init__` 方法）
```python
self.weight = 'delay'  # 从 'hop' 改为 'delay'
```

#### 3.3 实现 ARP 环路检测（与任务一相同）
```python
def handle_arp(self, msg, in_port, dst, src, pkt, pkt_type):
    """Handle ARP packets and prevent ARP loop"""
    # 环路检测逻辑
```

#### 3.4 实现路径时延计算（`handle_ipv4` 方法）
```python
# Calculate path delay and RTT
link_delay_dict = {}
path_delay = 0.0

# 遍历路径中的每条链路
for i in range(1, len(dpid_path) - 1):
    # 从拓扑图获取时延
    delay = self.network_awareness.topo_map[src][dst].get('delay', 0)
    link_delay_dict[f"s{src}->s{dst}"] = delay * 1000
    path_delay += delay

# 计算 RTT（往返时间）
path_RTT = path_delay * 2

# 输出结果
self.logger.info('link delay dict: %s', link_delay_dict)
self.logger.info("path delay = %.5fms", path_delay * 1000)
self.logger.info("path RTT = %.5fms", path_RTT * 1000)
```

#### 3.5 添加链路故障容忍（任务三，新增方法）
```python
@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
def port_status_handler(self, ev):
    """Handle port status change events"""
    # 检测端口状态变化
    # 清空拓扑图
    # 删除所有流表
    # 清空 sw 和 mac_to_port

def delete_flow(self, datapath, port_no):
    """Delete flow entries for a specific port"""
    # 删除 in_port 匹配的流表
    # 删除 out_port 匹配的流表

def delete_all_flow(self):
    """Delete all flow entries on all switches"""
    # 遍历所有交换机
    # 删除所有流表
```

**验证方法：**
```bash
uv run osken-manager shortest_delay.py --observe-links
# 在 Mininet 中：
# h2 ping h9  (查看 path delay 和 path RTT)
# link s6 s7 down  (测试故障切换)
# link s6 s7 up    (测试故障恢复)
```

---

## 🔧 需要修改的 OS-Ken 源文件

### 文件路径
```
.venv/lib/python3.13/site-packages/os_ken/topology/switches.py
```

### 修改 1：PortData 类
```python
class PortData(object):
    def __init__(self, is_down, lldp_data):
        super(PortData, self).__init__()
        self.is_down = is_down
        self.lldp_data = lldp_data
        self.timestamp = None    # 新增
        self.sent = 0
        self.delay = 0           # 新增
```

### 修改 2：lldp_packet_in_handler 方法
```python
@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
def lldp_packet_in_handler(self, ev):
    recv_timestamp = time.time()  # 新增
    
    # ... 原有代码 ...
    
    # 新增：计算 LLDP 时延
    for port, port_data in self.ports.items():
        if src_dpid == port.dpid and src_port_no == port.port_no:
            send_timestamp = port_data.timestamp
            if send_timestamp:
                port_data.delay = recv_timestamp - send_timestamp
```

**详细说明：** 查看 `OSKEN_MODIFICATION.md`

---

## 📊 功能对照表

| 任务 | 文件 | 功能 | 状态 |
|-----|------|------|------|
| 任务一 | `least_hops.py` | ARP 环路检测 | ✅ 完成 |
| 任务一 | `least_hops.py` | 最少跳数路径 | ✅ 完成 |
| 任务二 | `network_awareness.py` | LLDP 时延获取 | ✅ 完成 |
| 任务二 | `network_awareness.py` | Echo RTT 测量 | ✅ 完成 |
| 任务二 | `network_awareness.py` | 链路时延计算 | ✅ 完成 |
| 任务二 | `shortest_delay.py` | 最小时延路径 | ✅ 完成 |
| 任务二 | `shortest_delay.py` | 路径时延输出 | ✅ 完成 |
| 任务三 | `shortest_delay.py` | 端口状态监听 | ✅ 完成 |
| 任务三 | `shortest_delay.py` | 流表删除 | ✅ 完成 |
| 任务三 | `shortest_delay.py` | 故障自动恢复 | ✅ 完成 |

---

## 🎯 关键实现要点

### 任务一：ARP 环路检测
- **数据结构**：`self.sw = {(dpid, src_mac, dst_mac): in_port}`
- **检测逻辑**：如果同一个 key 从不同端口到达 → 环路
- **处理方式**：丢弃环路包（`return`）

### 任务二：链路时延测量
- **LLDP 时延**：从 switches 实例的 `port_data.delay` 获取
- **Echo RTT**：发送 Echo 请求，接收回复计算时间差
- **链路时延公式**：
  ```
  delay = max((T_lldp12 + T_lldp21 - T_echo1 - T_echo2) / 2, 0)
  ```
- **权重切换**：将 `self.weight` 从 `'hop'` 改为 `'delay'`

### 任务三：链路故障容忍
- **事件捕获**：`EventOFPPortStatus`
- **清理策略**：清空拓扑图、删除流表、清空 sw/mac_to_port
- **不清理**：lldp_delay_table、echo_RTT_table（测量数据）
- **原因**：拓扑结构变化，旧流表失效；测量数据持续有效

---

## 📝 验证清单

### 任务一验证
- [ ] 控制器输出路径信息
- [ ] h2 能 ping 通 h9
- [ ] 没有 ARP 环路警告（或有环路检测日志）

### 任务二验证
- [ ] 控制器输出链路时延（Link: X -> Y, delay: ...ms）
- [ ] 控制器输出 link delay dict
- [ ] 控制器输出 path delay 和 path RTT
- [ ] Ping RTT 与计算值接近（误差 < 10%）

### 任务三验证
- [ ] `link s6 s7 down` 后路径自动切换
- [ ] RTT 增加（约 270ms → 370ms）
- [ ] `link s6 s7 up` 后路径自动恢复
- [ ] RTT 恢复（约 370ms → 270ms）
- [ ] 控制器输出 "Topology map cleared"
- [ ] 控制器输出 "All flow entries deleted"

---

## 🐛 已处理的问题

1. **时延负值**：使用 `max(delay, 0)` 确保非负
2. **异步问题**：使用 `dict.get(key, default)` 处理键不存在
3. **Echo data 类型**：使用 `.encode('utf-8')` 转换为 bytes
4. **流表删除**：删除 in_port 和 out_port 两类流表
5. **环路检测**：使用三元组 `(dpid, src, dst)` 作为唯一键

---

## 📖 参考文档

- 详细实验指导：`README.md`
- 快速开始指南：`QUICKSTART.md`
- OS-Ken 修改说明：`OSKEN_MODIFICATION.md`

---

**所有代码修改已完成！** ✅

现在可以开始运行实验了。按照 `QUICKSTART.md` 中的步骤进行测试。

