#!/usr/bin/python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node, Host  # Using Host for routers is okay if configured
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info

# Use a helper class for Router nodes to automatically enable IP forwarding
class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        info(f'Enabling IP forwarding on {self.name}\n')
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class L3Topo(Topo):
    """
    Topology: 3 routers (A, B, C) connected in a triangle.
    Each router connects to a switch for its LAN.
    Each LAN switch connects to 2 hosts.
    LAN A: 20.10.172.128/26 (Router A is gateway)
    LAN B: 20.10.172.0/25   (Router B is gateway)
    LAN C: 20.10.172.192/27 (Router C is gateway)
    Inter-router links use 20.10.100.0/24.
    """
    def build(self, **_opts):

        # --- Define IP Addresses ---
        # Router gateway IPs for each LAN (using the first usable IP)
        ip_gw_lanA = '20.10.172.129/26'
        ip_gw_lanB = '20.10.172.1/25'
        ip_gw_lanC = '20.10.172.193/27'

        # Host IPs (starting after the gateway)
        ip_hA1 = '20.10.172.130/26'
        ip_hA2 = '20.10.172.131/26'
        ip_hB1 = '20.10.172.2/25'
        ip_hB2 = '20.10.172.3/25'
        ip_hC1 = '20.10.172.194/27'
        ip_hC2 = '20.10.172.195/27'

        # IPs for inter-router links
        ip_rA_rB = '20.10.100.1/24'
        ip_rB_rA = '20.10.100.2/24'
        ip_rB_rC = '20.10.100.3/24'
        ip_rC_rB = '20.10.100.4/24'
        ip_rC_rA = '20.10.100.5/24'
        ip_rA_rC = '20.10.100.6/24'

        # Extract gateway IPs for host default routes
        gw_A = ip_gw_lanA.split('/')[0]
        gw_B = ip_gw_lanB.split('/')[0]
        gw_C = ip_gw_lanC.split('/')[0]

        # --- Create Nodes ---
        # Add Routers using the LinuxRouter class
        rA = self.addNode('rA', cls=LinuxRouter, ip=None) # IP set per-interface
        rB = self.addNode('rB', cls=LinuxRouter, ip=None)
        rC = self.addNode('rC', cls=LinuxRouter, ip=None)

        # Add Switches for each LAN
        sA = self.addSwitch('sA')
        sB = self.addSwitch('sB')
        sC = self.addSwitch('sC')

        # Add Hosts, specifying IP and default gateway
        hA1 = self.addHost('hA1', ip=ip_hA1, defaultRoute=f'via {gw_A}')
        hA2 = self.addHost('hA2', ip=ip_hA2, defaultRoute=f'via {gw_A}')
        hB1 = self.addHost('hB1', ip=ip_hB1, defaultRoute=f'via {gw_B}')
        hB2 = self.addHost('hB2', ip=ip_hB2, defaultRoute=f'via {gw_B}')
        hC1 = self.addHost('hC1', ip=ip_hC1, defaultRoute=f'via {gw_C}')
        hC2 = self.addHost('hC2', ip=ip_hC2, defaultRoute=f'via {gw_C}')

        # --- Create Links ---
        # Link Hosts to their LAN Switches
        self.addLink(hA1, sA)
        self.addLink(hA2, sA)
        self.addLink(hB1, sB)
        self.addLink(hB2, sB)
        self.addLink(hC1, sC)
        self.addLink(hC2, sC)

        # Link LAN Switches to their respective Routers
        # Assign the gateway IP to the router's interface connected to the switch
        # intfName references are important for clarity. e.g., rA-eth0 connects to LAN A
        self.addLink(sA, rA, intfName1='sA-eth1', intfName2='rA-eth0', params2={'ip': ip_gw_lanA})
        self.addLink(sB, rB, intfName1='sB-eth1', intfName2='rB-eth0', params2={'ip': ip_gw_lanB})
        self.addLink(sC, rC, intfName1='sC-eth1', intfName2='rC-eth0', params2={'ip': ip_gw_lanC})

        # Link Routers to each other (triangle)
        # Assign IPs to both ends of the link
        # e.g., rA-eth1 connects to rB-eth1
        self.addLink(rA, rB, intfName1='rA-eth1', params1={'ip': ip_rA_rB},
                           intfName2='rB-eth1', params2={'ip': ip_rB_rA})
        self.addLink(rB, rC, intfName1='rB-eth2', params1={'ip': ip_rB_rC},
                           intfName2='rC-eth1', params2={'ip': ip_rC_rB})
        self.addLink(rC, rA, intfName1='rC-eth2', params1={'ip': ip_rC_rA},
                           intfName2='rA-eth2', params2={'ip': ip_rA_rC})

def run():
    "Create and test the L3 network"
    topo = L3Topo()
    # Use default Host class for hosts, LinuxRouter for routers (defined in topo)
    net = Mininet(topo=topo, link=TCLink, controller=None) # No SDN controller needed

    net.start()

    info("\n*** Network Started ***\n")
    info("*** Router IP Forwarding should be enabled via LinuxRouter class ***\n")

    # Routers automatically have routes to directly connected networks.
    # For full inter-LAN reachability, static routes would be needed on routers.
    # Example (add inside run() if needed):
    # info("Adding static routes...\n")
    # net['rA'].cmd('ip route add 20.10.172.0/25 via 20.10.100.2') # LAN B via rB
    # net['rA'].cmd('ip route add 20.10.172.192/27 via 20.10.100.5') # LAN C via rC
    # net['rB'].cmd('ip route add 20.10.172.128/26 via 20.10.100.1') # LAN A via rA
    # net['rB'].cmd('ip route add 20.10.172.192/27 via 20.10.100.4') # LAN C via rC
    # net['rC'].cmd('ip route add 20.10.172.128/26 via 20.10.100.6') # LAN A via rA
    # net['rC'].cmd('ip route add 20.10.172.0/25 via 20.10.100.3') # LAN B via rB

    info("\n=== Testing connectivity WITHIN each LAN ===\n")

    # Get host objects
    hA1, hA2 = net.get('hA1', 'hA2')
    hB1, hB2 = net.get('hB1', 'hB2')
    hC1, hC2 = net.get('hC1', 'hC2')

    # Perform pings between hosts on the same LAN
    # net.ping returns the overall packet loss percentage for the pairs
    info("--- Testing LAN A (hA1 <-> hA2) ---\n")
    loss = net.ping([hA1, hA2])
    info(f"LAN A Ping Loss: {loss}%\n")


    info("\n--- Testing LAN B (hB1 <-> hB2) ---\n")
    loss = net.ping([hB1, hB2])
    info(f"LAN B Ping Loss: {loss}%\n")

    info("\n--- Testing LAN C (hC1 <-> hC2) ---\n")
    loss = net.ping([hC1, hC2])
    info(f"LAN C Ping Loss: {loss}%\n")

    # Task 2 only required testing *intra*-LAN connectivity.
    # If static routes were added, you could test inter-LAN here:
    # info("\n=== Testing connectivity BETWEEN LANs (requires static routes) ===\n")
    # loss = net.ping([hA1, hB1]) # Example: hA1 to hB1
    # info(f"hA1 <-> hB1 Ping Loss: {loss}%\n")


    CLI(net) # Start CLI for interactive commands
    net.stop() # Stop network when CLI exits

if __name__ == '__main__':
    setLogLevel('info')
    run()