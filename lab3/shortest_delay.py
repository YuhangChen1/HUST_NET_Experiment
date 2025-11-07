from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER, HANDSHAKE_DISPATCHER
from os_ken.controller.handler import set_ev_cls
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet
from os_ken.lib.packet import ethernet, arp, ipv4, ether_types
from os_ken.topology import event
from os_ken.topology.api import get_all_switch
import sys
from network_awareness import NetworkAwareness
import networkx as nx
ETHERNET = ethernet.ethernet.__name__
ETHERNET_MULTICAST = "ff:ff:ff:ff:ff:ff"
ARP = arp.arp.__name__
class ShortestDelay(app_manager.OSKenApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {
        'network_awareness': NetworkAwareness
    }

    def __init__(self, *args, **kwargs):
        super(ShortestDelay, self).__init__(*args, **kwargs)
        self.network_awareness = kwargs['network_awareness']
        self.weight = 'delay'  # Changed to 'delay' for minimum delay path
        self.mac_to_port = {}
        self.sw = {}
        self.path = None
        self.last_port_status_time = {}  # Track last port status change time to avoid duplicate processing

    def add_flow(self, datapath, priority, match, actions, idle_timeout=0, hard_timeout=0):
        dp = datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        inst = [parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=dp, priority=priority,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
            match=match, instructions=inst)
        dp.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        parser = dp.ofproto_parser

        dpid = dp.id
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)

        pkt_type = eth_pkt.ethertype

        # layer 2 self-learning
        dst_mac = eth_pkt.dst
        src_mac = eth_pkt.src


        if isinstance(arp_pkt, arp.arp):
            self.handle_arp(msg, in_port, dst_mac,src_mac, pkt,pkt_type)

        if isinstance(ipv4_pkt, ipv4.ipv4):
            self.handle_ipv4(msg, in_port, ipv4_pkt.src, ipv4_pkt.dst, pkt_type)

    def handle_arp(self, msg, in_port, dst, src, pkt, pkt_type):
        """
        Handle ARP packets and prevent ARP loop using (dpid, src_mac, dst_mac) -> in_port mapping
        """
        datapath = msg.datapath
        dpid = datapath.id
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        
        # Get ARP packet to extract IP addresses
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            self.logger.info(
                "ARP packet: dpid=%s, src_ip=%s, dst_ip=%s, src_mac=%s, dst_mac=%s, in_port=%s",
                dpid, arp_pkt.src_ip, arp_pkt.dst_ip, src, dst, in_port
            )
        
        # Create unique key for ARP loop detection
        key = (dpid, src, dst)
        
        # Check for ARP loop
        if key in self.sw:
            if self.sw[key] != in_port:
                # Loop detected! Drop the packet
                self.logger.info(
                    "ARP loop detected: dpid=%s, src=%s, dst=%s, in_port=%s (previous=%s)",
                    dpid, src, dst, in_port, self.sw[key]
                )
                return  # Drop the packet
        else:
            # First time seeing this ARP request, record it
            self.sw[key] = in_port
        
        # Flood ARP packet
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)
        self.logger.info("ARP packet flooded from switch %s, port %s", dpid, in_port)

    def handle_ipv4(self, msg, in_port, src_ip, dst_ip, pkt_type):
        parser = msg.datapath.ofproto_parser

        dpid_path = self.network_awareness.shortest_path(src_ip, dst_ip,weight=self.weight)
        if not dpid_path:
            self.logger.warning(
                "No path found from %s to %s, topology may be re-discovering. "
                "Topo map edges: %d, link_info entries: %d",
                src_ip, dst_ip,
                len(self.network_awareness.topo_map.edges()),
                len(self.network_awareness.link_info)
            )
            return
        
        self.logger.info("Path found: %s", dpid_path)



        self.path=dpid_path
        # get port path:  h1 -> in_port, s1, out_port -> h2
        port_path = []
        for i in range(1, len(dpid_path) - 1):
            # Check if link_info exists (topology may be re-discovering)
            in_key = (dpid_path[i], dpid_path[i - 1])
            out_key = (dpid_path[i], dpid_path[i + 1])
            
            if in_key not in self.network_awareness.link_info or out_key not in self.network_awareness.link_info:
                self.logger.warning(
                    "Link info not ready for path %s, topology may be re-discovering. "
                    "Missing keys: in_key=%s (exists: %s), out_key=%s (exists: %s). "
                    "Total link_info entries: %d",
                    dpid_path,
                    in_key, in_key in self.network_awareness.link_info,
                    out_key, out_key in self.network_awareness.link_info,
                    len(self.network_awareness.link_info)
                )
                return
            
            switch_in_port = self.network_awareness.link_info[in_key]
            switch_out_port = self.network_awareness.link_info[out_key]
            port_path.append((switch_in_port, dpid_path[i], switch_out_port))
        self.show_path(src_ip, dst_ip, port_path)

        # Calculate path delay and RTT
        link_delay_dict = {}
        path_delay = 0.0
        
        # Calculate delay for each link in the path (including host-switch edges)
        for i in range(len(dpid_path) - 1):
            src = dpid_path[i]
            dst = dpid_path[i + 1]
            
            # Get delay from topo_map
            if self.network_awareness.topo_map.has_edge(src, dst):
                delay = self.network_awareness.topo_map[src][dst].get('delay', 0)
                # Format link name
                if isinstance(src, str):  # Host IP
                    link_name = f"h{src.split('.')[-1]}->s{dst}"
                elif isinstance(dst, str):  # Host IP
                    link_name = f"s{src}->h{dst.split('.')[-1]}"
                else:  # Switch to switch
                    link_name = f"s{src}->s{dst}"
                link_delay_dict[link_name] = delay * 1000  # Convert to ms
                path_delay += delay
        
        # Calculate path RTT (round-trip time = 2 * one-way delay)
        path_RTT = path_delay * 2
        
        # Output results
        self.logger.info('link delay dict: %s', link_delay_dict)
        self.logger.info("path delay = %.5fms", path_delay * 1000)
        self.logger.info("path RTT = %.5fms", path_RTT * 1000)

        # send flow mod
        for node in port_path:
            switch_in_port, dpid, switch_out_port = node
            self.send_flow_mod(parser, dpid, pkt_type, src_ip, dst_ip, switch_in_port, switch_out_port)
            self.send_flow_mod(parser, dpid, pkt_type, dst_ip, src_ip, switch_out_port, switch_in_port)

        # send packet_out
        _, dpid, out_port = port_path[-1]
        dp = self.network_awareness.switch_info[dpid]
        actions = [parser.OFPActionOutput(out_port)]
        out = parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=msg.data)
        dp.send_msg(out)

    def send_flow_mod(self, parser, dpid, pkt_type, src_ip, dst_ip, in_port, out_port):
        dp = self.network_awareness.switch_info[dpid]
        match = parser.OFPMatch(
            in_port=in_port, eth_type=pkt_type, ipv4_src=src_ip, ipv4_dst=dst_ip)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(dp, 1, match, actions, 10, 30)

    def show_path(self, src, dst, port_path):
        self.logger.info('path: {} -> {}'.format(src, dst))
        path = src + ' -> '
        for node in port_path:
            path += '{}:s{}:{}'.format(*node) + ' -> '
        path += dst
        self.logger.info(path)
    
    # ========== Task 3: Link Failure Tolerance ==========
    
    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        """Handle port status change events (link up/down)"""
        import time
        
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        
        if msg.reason in [ofproto.OFPPR_ADD, ofproto.OFPPR_MODIFY]:
            # Port added or modified (both link up and down are modifications)
            datapath.ports[msg.desc.port_no] = msg.desc
            
            # Create a unique key for this port status change
            port_key = (datapath.id, msg.desc.port_no)
            current_time = time.time()
            
            # Avoid processing duplicate events within 2 seconds
            if port_key in self.last_port_status_time:
                time_diff = current_time - self.last_port_status_time[port_key]
                if time_diff < 2.0:
                    self.logger.info(
                        "Ignoring duplicate port status event for switch %s, port %s (last event %.2f seconds ago)",
                        datapath.id, msg.desc.port_no, time_diff
                    )
                    return
            
            # Record this event time
            self.last_port_status_time[port_key] = current_time
            
            self.logger.info(
                "Port status changed on switch %s, port %s",
                datapath.id, msg.desc.port_no
            )
            
            # Clear data structures
            # 1. Clear topology map
            self.network_awareness.topo_map.clear()
            self.logger.info("Topology map cleared")
            
            # 2. Clear link_info (port mappings may be invalid)
            self.network_awareness.link_info.clear()
            self.logger.info("Link info cleared")
            
            # 3. Clear port_info and port_link (topology discovery data)
            self.network_awareness.port_info.clear()
            self.network_awareness.port_link.clear()
            self.logger.info("Port info and port link cleared")
            
            # 4. Delete all flow entries
            self.delete_all_flow()
            self.logger.info("All flow entries deleted")
            
            # 5. Clear sw (ARP loop detection table)
            self.sw.clear()
            
            # 6. Clear mac_to_port (self-learning table)
            self.mac_to_port.clear()
            
            self.logger.info("All data structures cleared, waiting for topology re-discovery...")
            
        elif msg.reason == ofproto.OFPPR_DELETE:
            datapath.ports.pop(msg.desc.port_no, None)
        else:
            return
    
    def delete_flow(self, datapath, port_no):
        """Delete flow entries associated with a specific port"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        try:
            # Delete flows matching in_port
            match_in = parser.OFPMatch(in_port=port_no)
            mod_in = parser.OFPFlowMod(
                datapath=datapath,
                command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY,
                out_group=ofproto.OFPG_ANY,
                match=match_in
            )
            datapath.send_msg(mod_in)
            
            # Delete flows with out_port matching port_no
            match_out = parser.OFPMatch()
            mod_out = parser.OFPFlowMod(
                datapath=datapath,
                command=ofproto.OFPFC_DELETE,
                out_port=port_no,
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
    
    def delete_all_flow(self):
        """Delete all flow entries on all switches"""
        switches = get_all_switch(self.network_awareness)
        
        for switch in switches:
            datapath = switch.dp
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            
            # Construct empty match (matches all flows)
            match = parser.OFPMatch()
            
            # Send delete command
            mod = parser.OFPFlowMod(
                datapath=datapath,
                command=ofproto.OFPFC_DELETE,
                out_port=ofproto.OFPP_ANY,
                out_group=ofproto.OFPG_ANY,
                match=match
            )
            datapath.send_msg(mod)
            
            # Reinstall default flow table to send packets to controller
            match = parser.OFPMatch()
            actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
            self.add_flow(datapath, 0, match, actions)
            
            self.logger.info("Deleted all flows on switch %s and reinstalled default flow", datapath.id)