from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet
from os_ken.lib.packet import arp
from os_ken.lib.packet import ether_types

ETHERNET = ethernet.ethernet.__name__
ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__


class Switch_Dict(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Switch_Dict, self).__init__(*args, **kwargs)
        self.flag = 0 # only modify once
        # maybe you need a global data structure to save the mapping
        # just data structure in mission 1
        # 维护 MAC 地址到端口的映射表: {dpid: {mac: port}}
        self.mac_to_port = {}
            

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=dp, priority=priority,
                                idle_timeout=idle_timeout,
                                hard_timeout=hard_timeout,
                                match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)]
        self.add_flow(dp, 0, match, actions)
                


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        # the identity of switch
        dpid = dp.id
        # the port that receive the packet
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        if eth_pkt.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        if eth_pkt.ethertype == ether_types.ETH_TYPE_IPV6:
            return
        # get the mac
        dst = eth_pkt.dst
        src = eth_pkt.src
        
        # you need to code here to avoid broadcast loop to finish mission 2
        # 禁用 s1 的某个端口来打破环路
        # 需要先运行 self_learning_switch.py 找出 s1 连接 s3 和 s4 的端口号
        if dpid == 1 and self.flag == 0:
            # TODO: 根据实际网络拓扑，修改 target_port 为需要禁用的端口号
            # 例如：如果 s1 的端口 2 连接到 s3，可以禁用端口 2
            # 或者：如果 s1 的端口 3 连接到 s4，可以禁用端口 3
            target_port = 3  # 请根据实际情况修改这个值（场景1用3，场景2用4）
            
            # 构造 OFPPortMod 消息来禁用端口
            port_mod = parser.OFPPortMod(
                datapath=dp,
                port_no=target_port,
                hw_addr='00:00:00:00:00:00',  # 会被 OVS 忽略
                config=ofp.OFPPC_PORT_DOWN,   # 禁用端口
                mask=ofp.OFPPC_PORT_DOWN      # 只修改 PORT_DOWN 标志
            )
            dp.send_msg(port_mod)
            
            # 等待消息发送完成
            import time
            time.sleep(0.5)
            
            self.flag = 1  # 标记已修改，避免重复操作
            self.logger.info("Port %s on switch %s has been disabled to break the loop", target_port, dpid)

        # self-learning
        # you need to code here to avoid the direct flooding
        # having fun
        # :)
        # just code in mission 1
        
        # 初始化该交换机的 MAC 表（如果还没有）
        self.mac_to_port.setdefault(dpid, {})
        
        # 学习源 MAC 地址和入端口的映射
        self.mac_to_port[dpid][src] = in_port
        
        # 查询目的 MAC 地址是否已学习
        if dst in self.mac_to_port[dpid]:
            # 映射表命中，获取输出端口
            out_port = self.mac_to_port[dpid][dst]
            
            # 打印五元组信息
            self.logger.info("Packet matched: dpid=%s, src=%s, in_port=%s, dst=%s, out_port=%s", 
                           dpid, src, in_port, dst, out_port)
            
            # 构造匹配规则和动作
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            actions = [parser.OFPActionOutput(out_port)]
            
            # 下发流表
            self.add_flow(dp, 1, match, actions)
            
            # 转发当前数据包
            out = parser.OFPPacketOut(
                datapath=dp,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            dp.send_msg(out)
        else:
            # 映射表未命中，洪泛
            actions = [parser.OFPActionOutput(ofp.OFPP_FLOOD)]
            out = parser.OFPPacketOut(
                datapath=dp,
                buffer_id=msg.buffer_id,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            dp.send_msg(out)