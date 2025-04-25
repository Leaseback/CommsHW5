from mininet.net import Mininet
from mininet.node import Host
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink


class Layer3Topo(Topo):
    def build(self):
        # Routers
        routerA = self.addHost('A')
        routerB = self.addHost('B')
        routerC = self.addHost('C')

        # Hosts
        hostA1 = self.addHost('A1', ip='20.10.172.1/26')
        hostA2 = self.addHost('A2', ip='20.10.172.2/26')
        hostB1 = self.addHost('B1', ip='20.10.172.65/25')
        hostB2 = self.addHost('B2', ip='20.10.172.66/25')
        hostC1 = self.addHost('C1', ip='20.10.172.193/27')
        hostC2 = self.addHost('C2', ip='20.10.172.194/27')

        # LAN links
        self.addLink(hostA1, routerA)
        self.addLink(hostA2, routerA)
        self.addLink(hostB1, routerB)
        self.addLink(hostB2, routerB)
        self.addLink(hostC1, routerC)
        self.addLink(hostC2, routerC)

        # Inter-router links
        self.addLink(routerA, routerB)
        self.addLink(routerB, routerC)
        self.addLink(routerA, routerC)


def run():
    topo = Layer3Topo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Routers
    A = net.get('A')
    B = net.get('B')
    C = net.get('C')

    # Enable IP forwarding
    for r in [A, B, C]:
        r.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Assign router interface IPs
    A.setIP('20.10.172.3/26', intf='A-eth0')  # To A1
    A.setIP('20.10.172.4/26', intf='A-eth1')  # To A2
    A.setIP('20.10.100.1/24', intf='A-eth2')  # To B
    A.setIP('20.10.100.3/24', intf='A-eth3')  # To C

    B.setIP('20.10.172.67/25', intf='B-eth0')  # To B1
    B.setIP('20.10.172.68/25', intf='B-eth1')  # To B2
    B.setIP('20.10.100.2/24', intf='B-eth2')  # To A
    B.setIP('20.10.100.4/24', intf='B-eth3')  # To C

    C.setIP('20.10.172.195/27', intf='C-eth0')  # To C1
    C.setIP('20.10.172.196/27', intf='C-eth1')  # To C2
    C.setIP('20.10.100.5/24', intf='C-eth2')  # To A
    C.setIP('20.10.100.6/24', intf='C-eth3')  # To B

    # Add static routes
    A.cmd("ip route add 20.10.172.64/25 via 20.10.100.2 dev A-eth2")
    A.cmd("ip route add 20.10.172.192/27 via 20.10.100.6 dev A-eth3")

    B.cmd("ip route add 20.10.172.0/26 via 20.10.100.1 dev B-eth2")
    B.cmd("ip route add 20.10.172.192/27 via 20.10.100.6 dev B-eth3")

    C.cmd("ip route add 20.10.172.0/26 via 20.10.100.3 dev C-eth2")
    C.cmd("ip route add 20.10.172.64/25 via 20.10.100.4 dev C-eth3")



    CLI(net)
    net.stop()


if __name__ == '__main__':
    run()
