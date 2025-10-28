#!/usr/bin/env python3
"""
FAT TREE Topology for k=4
Implementation of a k=4 Fat Tree topology using Mininet Python API

Network Structure for k=4:
- 4 Pods
- Each Pod has:
  - Edge layer: 2 switches (k/2 = 2), each with 4 ports
    - Ports 0-1: connected to hosts (k/2 = 2 hosts per edge switch)
    - Ports 2-3: connected to aggregation switches
  - Aggregation layer: 2 switches (k/2 = 2), each with 4 ports
    - Ports 0-1: connected to edge switches
    - Ports 2-3: connected to core switches
- Core layer: 4 switches ((k/2)^2 = 4), arranged in 2x2 array

Total hosts: 4 pods * 2 edge switches * 2 hosts = 16 hosts
Total switches: 4 pods * (2 edge + 2 agg) + 4 core = 4*4 + 4 = 20 switches
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info


class FatTreeTopo(Topo):
    def __init__(self, k=4):
        """
        Create a Fat Tree topology with parameter k
        Default k=4 as required by the experiment
        """
        super(FatTreeTopo, self).__init__()

        self.k = k
        self.pod_num = k
        self.edge_switches_per_pod = k // 2
        self.agg_switches_per_pod = k // 2
        self.core_switches = (k // 2) ** 2

        # Create all switches and hosts
        self._create_switches()
        self._create_hosts()
        self._create_links()

    def _create_switches(self):
        """Create all switches: edge, aggregation, and core"""
        self.edge_switches = []
        self.agg_switches = []
        self.core_switches_list = []

        # Create edge switches (2 per pod, 4 pods = 8 total)
        for pod in range(self.pod_num):
            pod_edges = []
            for edge in range(self.edge_switches_per_pod):
                switch_name = f'e{pod}{edge}'
                switch = self.addSwitch(switch_name)
                pod_edges.append(switch)
            self.edge_switches.append(pod_edges)

        # Create aggregation switches (2 per pod, 4 pods = 8 total)
        for pod in range(self.pod_num):
            pod_aggs = []
            for agg in range(self.agg_switches_per_pod):
                switch_name = f'a{pod}{agg}'
                switch = self.addSwitch(switch_name)
                pod_aggs.append(switch)
            self.agg_switches.append(pod_aggs)

        # Create core switches (4 total for k=4)
        for core_idx in range(self.core_switches):
            switch_name = f'c{core_idx}'
            switch = self.addSwitch(switch_name)
            self.core_switches_list.append(switch)

    def _create_hosts(self):
        """Create hosts: 2 hosts per edge switch"""
        self.hosts_list = []
        host_count = 0

        for pod in range(self.pod_num):
            pod_hosts = []
            for edge in range(self.edge_switches_per_pod):
                edge_hosts = []
                for host in range(self.k // 2):  # 2 hosts per edge switch for k=4
                    host_name = f'h{host_count + 1}'
                    host_ip = f'10.{pod + 1}.{edge + 1}.{host + 1}'
                    host_node = self.addHost(host_name, ip=host_ip)
                    edge_hosts.append(host_node)
                    host_count += 1
                pod_hosts.append(edge_hosts)
            self.hosts_list.append(pod_hosts)

    def _create_links(self):
        """Create all links according to Fat Tree topology rules"""
        self._create_edge_to_host_links()
        self._create_edge_to_agg_links()
        self._create_agg_to_core_links()

    def _create_edge_to_host_links(self):
        """Connect edge switches to hosts (ports 0-1 of edge switches)"""
        for pod in range(self.pod_num):
            for edge in range(self.edge_switches_per_pod):
                for host in range(self.k // 2):
                    host_node = self.hosts_list[pod][edge][host]
                    edge_switch = self.edge_switches[pod][edge]
                    self.addLink(host_node, edge_switch)

    def _create_edge_to_agg_links(self):
        """Connect edge switches to aggregation switches"""
        for pod in range(self.pod_num):
            for edge in range(self.edge_switches_per_pod):
                for agg in range(self.agg_switches_per_pod):
                    edge_switch = self.edge_switches[pod][edge]
                    agg_switch = self.agg_switches[pod][agg]
                    self.addLink(edge_switch, agg_switch)

    def _create_agg_to_core_links(self):
        """Connect aggregation switches to core switches"""
        # For k=4, core switches are arranged in 2x2 array
        # Each core switch connects to all pods, but specific agg switches

        for pod in range(self.pod_num):
            for agg in range(self.agg_switches_per_pod):
                # Each agg switch connects to k/2 = 2 core switches
                for core_group in range(self.k // 2):
                    core_idx = (agg * (self.k // 2) + core_group) % self.core_switches
                    agg_switch = self.agg_switches[pod][agg]
                    core_switch = self.core_switches_list[core_idx]
                    self.addLink(agg_switch, core_switch)


def run_fat_tree():
    """Run the Fat Tree topology without controller as required by experiment"""
    setLogLevel('info')

    # Clean up any previous Mininet state
    info("*** Cleaning up previous Mininet state ***\n")
    from mininet.clean import cleanup
    cleanup()

    # Create topology
    topo = FatTreeTopo(k=4)

    # Create network with OVS switches, NO controller (as required by experiment)
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None, autoSetMacs=True)

    # Start network without controller
    net.start()

    info("*** FAT TREE Topology (k=4) Started WITHOUT Controller ***\n")
    info("Network Information:\n")
    info("- 4 Pods\n")
    info("- 16 Hosts (h1-h16)\n")
    info("- 20 Switches (8 edge + 8 aggregation + 4 core)\n")
    info("- NO Controller (as required by experiment)\n")

    # Test connectivity with pingall
    info("*** Testing connectivity with pingall (this may take time) ***\n")
    result = net.pingAll()

    if result == 0:
        info("*** SUCCESS: All hosts are connected! ***\n")
        info("*** Analyzing data paths using ovs-appctl fdb/show ***\n")

        # Show MAC tables for analysis
        info("MAC tables for switches:\n")
        for switch in net.switches:
            info(f"--- {switch.name} MAC table ---\n")
            try:
                # Use ovs-appctl to show forwarding database
                output = switch.cmd(f"ovs-appctl fdb/show {switch.name}")
                info(output)
            except:
                info(f"Could not get MAC table for {switch.name}\n")

    else:
        info("*** FAILURE: Some hosts are not connected ***\n")
        info("*** Use Wireshark to analyze packet flow and debug connectivity ***\n")

    # Enter CLI for manual testing
    info("*** Entering Mininet CLI for manual testing and analysis ***\n")
    info("Available commands:\n")
    info("- pingall: Test all host connectivity\n")
    info("- h1 ping h2: Test specific host connectivity\n")
    info("- nodes: Show all nodes\n")
    info("- net: Show network topology\n")
    info("- dump: Show detailed node information\n")
    info("- xterm switch_name: Open terminal for switch (e.g., xterm e00)\n")
    info("- exit: Exit Mininet\n")
    info("*** Type commands at the 'mininet>' prompt ***\n")

    CLI(net)

    # Cleanup
    net.stop()


if __name__ == '__main__':
    run_fat_tree()
