#!/usr/bin/python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node, Host
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

# Use a helper class for Router nodes to automatically enable IP forwarding
class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        info(f'Enabling IP forwarding on {self.name}\n')
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class L3Topo(Topo):
    def build(self, **_opts):

        # --- Define IP Addresses ---
        ip_gw_lanA = '20.10.172.129/26'
        ip_gw_lanB = '20.10.172.1/25'
        ip_gw_lanC = '20.10.172.193/27'

        ip_hA1 = '20.10.172.130/26'
        ip_hA2 = '20.10.172.131/26'
        ip_hB1 = '20.10.172.2/25'
        ip_hB2 = '20.10.172.3/25'
        ip_hC1 = '20.10.172.194/27'
        ip_hC2 = '20.10.172.195/27'

        ip_rA_rB = '20.10.100.1/24'
        ip_rB_rA = '20.10.100.2/24'
        ip_rB_rC = '20.10.100.3/24'
        ip_rC_rB = '20.10.100.4/24'
        ip_rC_rA = '20.10.100.5/24'
        ip_rA_rC = '20.10.100.6/24'

        gw_A = ip_gw_lanA.split('/')[0]
        gw_B = ip_gw_lanB.split('/')[0]
        gw_C = ip_gw_lanC.split('/')[0]

        # --- Create Nodes ---
        rA = self.addNode('rA', cls=LinuxRouter, ip=None)
        rB = self.addNode('rB', cls=LinuxRouter, ip=None)
        rC = self.addNode('rC', cls=LinuxRouter, ip=None)

        # Use numeric switch names to avoid DPID error
        sA = self.addSwitch('s1')
        sB = self.addSwitch('s2')
        sC = self.addSwitch('s3')

        hA1 = self.addHost('hA1', ip=ip_hA1, defaultRoute=f'via {gw_A}')
        hA2 = self.addHost('hA2', ip=ip_hA2, defaultRoute=f'via {gw_A}')
        hB1 = self.addHost('hB1', ip=ip_hB1, defaultRoute=f'via {gw_B}')
        hB2 = self.addHost('hB2', ip=ip_hB2, defaultRoute=f'via {gw_B}')
        hC1 = self.addHost('hC1', ip=ip_hC1, defaultRoute=f'via {gw_C}')
        hC2 = self.addHost('hC2', ip=ip_hC2, defaultRoute=f'via {gw_C}')

        # --- Create Links ---
        self.addLink(hA1, sA)
        self.addLink(hA2, sA)
        self.addLink(hB1, sB)
        self.addLink(hB2, sB)
        self.addLink(hC1, sC)
        self.addLink(hC2, sC)

        self.addLink(sA, rA, intfName1='sA-eth1', intfName2='rA-eth0', params2={'ip': ip_gw_lanA})
        self.addLink(sB, rB, intfName1='sB-eth1', intfName2='rB-eth0', params2={'ip': ip_gw_lanB})
        self.addLink(sC, rC, intfName1='sC-eth1', intfName2='rC-eth0', params2={'ip': ip_gw_lanC})

        self.addLink(rA, rB, intfName1='rA-eth1', params1={'ip': ip_rA_rB},
                           intfName2='rB-eth1', params2={'ip': ip_rB_rA})
        self.addLink(rB, rC, intfName1='rB-eth2', params1={'ip': ip_rB_rC},
                           intfName2='rC-eth1', params2={'ip': ip_rC_rB})
        self.addLink(rC, rA, intfName1='rC-eth2', params1={'ip': ip_rC_rA},
                           intfName2='rA-eth2', params2={'ip': ip_rA_rC})

def run():
    topo = L3Topo()
    net = Mininet(topo=topo, link=TCLink, controller=None)

    net.start()

    info("\n*** Network Started ***\n")
    info("*** Router IP Forwarding should be enabled via LinuxRouter class ***\n")

    info("\n=== Testing connectivity WITHIN each LAN ===\n")

    hA1, hA2 = net.get('hA1', 'hA2')
    hB1, hB2 = net.get('hB1', 'hB2')
    hC1, hC2 = net.get('hC1', 'hC2')

    info("--- Testing LAN A (hA1 <-> hA2) ---\n")
    loss = net.ping([hA1, hA2])
    info(f"LAN A Ping Loss: {loss}%\n")

    info("\n--- Testing LAN B (hB1 <-> hB2) ---\n")
    loss = net.ping([hB1, hB2])
    info(f"LAN B Ping Loss: {loss}%\n")

    info("\n--- Testing LAN C (hC1 <-> hC2) ---\n")
    loss = net.ping([hC1, hC2])
    info(f"LAN C Ping Loss: {loss}%\n")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
