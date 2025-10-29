# Lab 3 实验报告模板 📋

## 实验信息

- **姓名**：___________
- **学号**：___________
- **日期**：___________
- **实验环境**：Ubuntu Linux (虚拟机)

---

## 一、实验目的

理解 SDN 网络中的链路发现和时延测量机制，掌握动态路径选择和故障恢复方法。

具体目标：
1. 理解 LLDP 协议在拓扑发现中的作用
2. 掌握链路时延测量原理（LLDP + Echo）
3. 学习使用 NetworkX 进行图算法计算
4. 实现网络故障自动检测和路径切换

---

## 二、实验环境

| 项目 | 版本/信息 |
|-----|----------|
| 操作系统 | Ubuntu Linux |
| Python 版本 | 3.13 |
| OS-Ken 版本 | ___ |
| Mininet 版本 | ___ |
| NetworkX 版本 | ___ |
| OpenFlow 版本 | 1.3 |

---

## 三、任务一：最少跳数路径

### 3.1 实验步骤

1. 启动拓扑：`sudo ./topo.py`
2. 启动控制器：`uv run osken-manager least_hops.py --observe-links`
3. 测试连通性：`h2 ping h9`

### 3.2 ARP 环路检测实现

**核心代码：**
```python
# 粘贴你的 handle_arp() 函数实现
```

**实现思路：**
- 使用 `(dpid, src_mac, dst_mac)` 作为唯一键
- 记录每个 ARP 请求的首次入端口
- 如果同一请求从不同端口到达，判定为环路并丢弃

### 3.3 实验结果

**控制器输出截图：**

[在此粘贴截图]

**路径信息：**
```
path: 10.0.0.2 -> 10.0.0.9
路径：h2 → s___ → s___ → s___ → s___ → h9
跳数：___ 跳
```

**Ping 结果：**
```
10 packets transmitted, ___ received, ___% packet loss
time ___ms
```

### 3.4 NetworkX 使用说明

**`shortest_simple_paths` API 解释：**
- **功能**：计算两点间的简单路径（无环），按成本排序
- **参数**：
  - `G`: 图对象
  - `source`: 源节点
  - `target`: 目标节点
  - `weight`: 权重属性名称（'hop' 或 'delay'）
- **返回值**：生成器，产生路径列表（节点序列）
- **示例**：
  ```python
  paths = list(nx.shortest_simple_paths(self.topo_map, src, dst, weight='hop'))
  shortest_path = paths[0]  # 第一条即为最短路径
  ```

---

## 四、任务二：最小时延路径

### 4.1 LLDP 时延测量原理

**链路时延计算公式：**

\[
\text{delay} = \max\left(\frac{T_{\text{lldp12}} + T_{\text{lldp21}} - T_{\text{echo1}} - T_{\text{echo2}}}{2}, 0\right)
\]

**原理说明：**

[在此画出或解释时延测量的原理图]

**T<sub>lldp</sub> 测量：**
- LLDP 包从控制器发出，经过 S1 → S2，返回控制器
- 记录往返时间 T<sub>lldp12</sub>

**T<sub>echo</sub> 测量：**
- Echo 请求从控制器发出，到达 S1，Echo 回复返回
- 记录往返时间 T<sub>echo1</sub>

**单向时延推导：**
```
T_lldp12 = T_echo1/2 + link_delay + T_echo2/2
T_lldp21 = T_echo2/2 + link_delay + T_echo1/2

相加：T_lldp12 + T_lldp21 = T_echo1 + T_echo2 + 2 * link_delay

解出：link_delay = (T_lldp12 + T_lldp21 - T_echo1 - T_echo2) / 2
```

### 4.2 代码实现

**关键代码片段：**

**1. LLDP 时延获取**
```python
# 粘贴 packet_in_handler 方法
```

**2. Echo 周期发送**
```python
# 粘贴 send_echo_request 和 examine_echo_RTT 方法
```

**3. Echo 回复处理**
```python
# 粘贴 handle_echo_reply 方法
```

**4. 链路时延计算**
```python
# 粘贴 calculate_link_delay 方法
```

### 4.3 实验结果

**链路时延测量结果：**

| 链路 | 时延 (ms) | 备注 |
|-----|----------|------|
| s2 → s4 | ___ | |
| s4 → s5 | ___ | |
| s5 → s6 | ___ | |
| s6 → s7 | ___ | 最优路径使用 |
| s7 → s8 | ___ | |
| s8 → s9 | ___ | |

**控制器输出截图：**

[粘贴链路时延输出截图]

**最小时延路径：**
```
path: 10.0.0.2 -> 10.0.0.9
路径：h2 → s___ → s___ → ... → s___ → h9

link delay dict: {___}
path delay = ___ms
path RTT = ___ms
```

**Ping 验证：**
```
64 bytes from 10.0.0.9: icmp_seq=1 ttl=64 time=___ ms
64 bytes from 10.0.0.9: icmp_seq=2 ttl=64 time=___ ms
...
平均 RTT：___ ms
```

**对比分析：**
- 计算的 path RTT：___ ms
- 实际 Ping RTT：___ ms
- 误差：___% （(实际 - 计算) / 计算 × 100%）
- 误差原因分析：___

### 4.4 遇到的问题与解决

**问题 1：时延出现负值**
- **现象**：___
- **原因**：___
- **解决方法**：___

**问题 2：___**
- **现象**：___
- **原因**：___
- **解决方法**：___

---

## 五、任务三：链路故障容忍

### 5.1 故障检测机制

**EventOFPPortStatus 事件说明：**
- **触发时机**：端口状态变化（link up/down）
- **reason 类型**：
  - `OFPPR_ADD`：端口新增
  - `OFPPR_MODIFY`：端口修改（包括 up/down）
  - `OFPPR_DELETE`：端口删除

**代码实现：**
```python
# 粘贴 port_status_handler 方法
```

### 5.2 故障恢复流程

**清理步骤：**
1. 清空拓扑图（`topo_map.clear()`）
2. 删除所有流表（`delete_all_flow()`）
3. 清空 ARP 检测表（`sw.clear()`）
4. 清空自学习表（`mac_to_port.clear()`）

**流表删除代码：**
```python
# 粘贴 delete_flow 和 delete_all_flow 方法
```

### 5.3 实验结果

**初始状态（s6-s7 正常）：**
```
路径：h2 → ... → s6 → s7 → s8 → s9 → h9
path delay = ___ ms
Ping RTT = ___ ms
```

**控制器输出截图：**
[粘贴初始状态截图]

**故障状态（s6-s7 down）：**
```
命令：link s6 s7 down

控制器输出：
Port status changed on switch ___, port ___
Topology map cleared
All flow entries deleted

新路径：h2 → ... → s5 → s9 → h9 (绕过 s6-s7)
path delay = ___ ms (增加)
Ping RTT = ___ ms
```

**控制器输出截图：**
[粘贴故障状态截图]

**Mininet 输出：**
```
Request timeout for icmp_seq ___
Request timeout for icmp_seq ___
64 bytes from 10.0.0.9: icmp_seq=___ ttl=64 time=___ ms
```

**恢复状态（s6-s7 up）：**
```
命令：link s6 s7 up

控制器输出：
Port status changed on switch ___, port ___
Topology map cleared
All flow entries deleted

恢复路径：h2 → ... → s6 → s7 → s8 → s9 → h9
path delay = ___ ms (恢复)
Ping RTT = ___ ms
```

**控制器输出截图：**
[粘贴恢复状态截图]

### 5.4 思考与分析（重点！）

**问题：为什么需要清空拓扑图、sw，而不需要清空 lldp_delay_table？**

**答案：**

**需要清空的数据结构：**

1. **topo_map（拓扑图）**：
   - 原因：___
   - 如果不清空会导致：___

2. **流表（Flow Table）**：
   - 原因：___
   - 如果不删除会导致：___

3. **sw（ARP 检测表）**：
   - 原因：___
   - 如果不清空会导致：___

4. **mac_to_port（自学习表）**：
   - 原因：___
   - 如果不清空会导致：___

**不需要清空的数据结构：**

1. **lldp_delay_table、echo_RTT_table**：
   - 原因：这些是**测量数据**，不是**拓扑结构**
   - 链路时延是链路的物理属性，不会因端口状态变化而失效
   - 保留这些数据可以加快恢复速度
   - LLDP 和 Echo 会持续测量，自动更新数据

**对比表：**

| 数据结构 | 是否清空 | 数据类型 | 原因 |
|---------|---------|---------|------|
| topo_map | ✅ 清空 | 拓扑结构 | ___ |
| 流表 | ✅ 删除 | 转发规则 | ___ |
| sw | ✅ 清空 | 控制数据 | ___ |
| mac_to_port | ✅ 清空 | 控制数据 | ___ |
| lldp_delay_table | ❌ 保留 | 测量数据 | ___ |
| echo_RTT_table | ❌ 保留 | 测量数据 | ___ |

---

## 六、实验总结

### 6.1 实验收获

（写出你在本实验中的收获，至少 3 点）

1. ___
2. ___
3. ___

### 6.2 对 SDN 的理解

（结合本实验，谈谈你对 SDN 控制与转发分离的理解）

___

### 6.3 环路问题的启示

（对比 Lab 2 的环路检测和 Lab 3 的拓扑发现，有什么新的理解？）

___

### 6.4 改进建议

（如果让你改进这个实验，你会怎么做？）

___

---

## 七、思考题

### 问题 1：如果网络中有多条相同时延的路径，控制器会如何选择？

**答案：**

___

### 问题 2：LLDP 无法发现主机，如何解决沉默主机问题？

**答案：**

___

### 问题 3：如果交换机与控制器之间的连接断开，网络会发生什么？

**答案：**

___

---

## 附录：实验截图

### 任务一截图（3 张）
1. [控制器输出]
2. [Ping 成功]
3. [ARP 环路检测日志（可选）]

### 任务二截图（6 张）
1. [链路时延测量]
2. [link delay dict]
3. [path delay 和 path RTT]
4. [Ping RTT 对比]
5. [代码实现 1]
6. [代码实现 2]

### 任务三截图（6 张）
1. [初始状态 - 控制器]
2. [初始状态 - Ping]
3. [故障状态 - 命令]
4. [故障状态 - 控制器]
5. [恢复状态 - 命令]
6. [恢复状态 - 控制器]

---

**实验完成日期**：___________

**报告撰写日期**：___________

