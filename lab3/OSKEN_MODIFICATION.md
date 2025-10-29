# OS-Ken 源文件修改说明

## 重要提示

任务二需要修改 OS-Ken 的源文件以支持 LLDP 时延测量。请按照以下步骤操作。

## 修改文件路径

```
.venv/lib/python3.13/site-packages/os_ken/topology/switches.py
```

## 修改内容

### 1. 修改 PortData 类

找到 `PortData` 类定义，添加以下两个属性：

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

### 2. 修改 lldp_packet_in_handler 方法

找到 `Switches` 类中的 `lldp_packet_in_handler` 方法，在开头添加时间戳记录，并在解析后计算延迟：

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
    
    # ... 原有代码继续 ...
```

### 3. 导入 time 模块

确保在文件顶部导入了 `time` 模块：

```python
import time
```

## 验证修改

修改完成后，可以通过以下方式验证：

1. 启动控制器时不应该有错误
2. 运行 `shortest_delay.py` 时应该能看到链路时延输出

## 如果修改失败

如果手动修改失败，可以：

1. 删除虚拟环境重新创建：
```bash
rm -rf .venv
uv sync
```

2. 或者删除 Python 缓存：
```bash
find .venv -name "*.pyc" -delete
find .venv -name "__pycache__" -type d -exec rm -rf {} +
```

## 注意事项

- 修改源文件前建议先备份
- 修改后需要重启控制器才能生效
- 如果使用 Git，不要提交 `.venv` 目录的修改

