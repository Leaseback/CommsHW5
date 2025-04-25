from mininet.net import Mininet
from mininet.node import Host
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink


class Layer3Topo(Topo):
    def build(self):
        # Create routers (as hosts)
        routerA = self.addHost('A')
        routerB = self.addHost('B')
        routerC = self.addHost('C')

        # Create hosts
        hostA1 = self.addHost('A1', ip='20.10.172.1/26')
        hostA2 = self.addHost('A2', ip='20.10.172.2/26')
        hostB1 = self.addHost('B1', ip='20.10.172.65/25')
        hostB2 = self.addHost('B2', ip='20.10.172.66/25')
        hostC1 = self.addHost('C1', ip='20.10.172.193/27')
        hostC2 = self.addHost('C2', ip='20.10.172.194/27')

        # Create switches (LANs)
        switchA = self.addSwitch('s1')
        switchB = self.addSwitch('s2')
        switchC = self.addSwitch('s3')

        # Connect LAN A
        self.addLink(hostA1, switchA)
        self.addLink(hostA2, switchA)
        self.addLink(routerA, switchA)

        # Connect LAN B
        self.addLink(hostB1, switchB)
        self.addLink(hostB2, switchB)
        self.addLink(routerB, switchB)

        # Connect LAN C
        self.addLink(hostC1, switchC)
        self.addLink(hostC2, switchC)
        self.addLink(routerC, switchC)

        # Connect routers directly
        self.addLink(routerA, routerB)  # A-eth1 <-> B-eth1
        self.addLink(routerB, routerC)  # B-eth2 <-> C-eth1
        self.addLink(routerA, routerC)  # A-eth2 <-> C-eth2


def run():
    topo = Layer3Topo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Get routers
    routerA = net.get('A')
    routerB = net.get('B')
    routerC = net.get('C')

    # Assign LAN IPs to routers
    routerA.setIP('20.10.172.3/26', intf='A-eth0')
    routerB.setIP('20.10.172.67/25', intf='B-eth0')
    routerC.setIP('20.10.172.195/27', intf='C-eth0')

    # Assign inter-router IPs
    routerA.setIP('20.10.100.1/24', intf='A-eth1')  # A <-> B
    routerA.setIP('20.10.100.3/24', intf='A-eth2')  # A <-> C
    routerB.setIP('20.10.100.2/24', intf='B-eth1')  # B <-> A
    routerB.setIP('20.10.100.4/24', intf='B-eth2')  # B <-> C
    routerC.setIP('20.10.100.5/24', intf='C-eth1')  # C <-> B
    routerC.setIP('20.10.100.6/24', intf='C-eth2')  # C <-> A

    # Enable IP forwarding
    for router in (routerA, routerB, routerC):
        router.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Add static routes
    routerA.cmd('ip route add 20.10.172.64/25 via 20.10.100.2 dev A-eth1')  # To LAN B
    routerA.cmd('ip route add 20.10.172.192/27 via 20.10.100.6 dev A-eth2')  # To LAN C

    routerB.cmd('ip route add 20.10.172.0/26 via 20.10.100.1 dev B-eth1')  # To LAN A
    routerB.cmd('ip route add 20.10.172.192/27 via 20.10.100.5 dev B-eth2')  # To LAN C

    routerC.cmd('ip route add 20.10.172.0/26 via 20.10.100.3 dev C-eth2')  # To LAN A
    routerC.cmd('ip route add 20.10.172.64/25 via 20.10.100.4 dev C-eth1')  # To LAN B

    CLI(net)
    net.stop()


if __name__ == '__main__':
    run()
