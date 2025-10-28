#!/usr/bin/env python3
"""
Debug script for FAT TREE topology
Enter Mininet CLI directly without automatic pingall
"""

from fat_tree_topo import FatTreeTopo
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.clean import cleanup


def debug_fat_tree():
    """Debug the Fat Tree topology - enter CLI directly"""
    setLogLevel('info')

    # Clean up any previous Mininet state
    info("*** Cleaning up previous Mininet state ***\n")
    cleanup()

    # Create topology
    topo = FatTreeTopo(k=4)

    # Create network with OVS switches, NO controller
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None, autoSetMacs=True)

    # Start network
    net.start()

    info("*** FAT TREE Topology (k=4) Started WITHOUT Controller ***\n")
    info("Network Information:\n")
    info("- 4 Pods\n")
    info("- 16 Hosts (h1-h16)\n")
    info("- 20 Switches (8 edge + 8 aggregation + 4 core)\n")
    info("- NO Controller (as required by experiment)\n")
    info("\n")
    info("*** You are now in MININET CLI ***\n")
    info("*** Type your commands at the 'mininet>' prompt below ***\n")
    info("\n")
    info("Useful commands:\n")
    info("- pingall: Test all connectivity\n")
    info("- h1 ping h2: Test specific hosts\n")
    info("- net: Show topology\n")
    info("- nodes: Show all nodes\n")
    info("- xterm e00: Open terminal for Wireshark\n")
    info("- exit: Exit Mininet\n")

    # Enter CLI immediately
    CLI(net)

    # Cleanup
    net.stop()


if __name__ == '__main__':
    debug_fat_tree()