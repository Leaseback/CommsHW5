from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

# Custom Node class to enable IP forwarding on routers
class Router(Node):
    def config(self, **params):
        super(Router, self).config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(Router, self).terminate()


class CustomLAN(Topo):
    def build(self):
        # Add routers (as custom nodes)
        rA = self.addNode('rA', cls=Router)
        rB = self.addNode('rB', cls=Router)
        rC = self.addNode('rC', cls=Router)

        # Add switches
        s1 = self.addSwitch('s1')  # LAN A
        s2 = self.addSwitch('s2')  # LAN B
        s3 = self.addSwitch('s3')  # LAN C

        # LAN A: 20.10.172.128/26
        for i in range(1, 4):
            ip = f'20.10.172.{128 + i}/26'
            self.addHost(f'hA{i}', ip=ip, defaultRoute='via 20.10.172.129')
            self.addLink(f'hA{i}', s1)

        # LAN B: 20.10.172.0/25
        for i in range(1, 4):
            ip = f'20.10.172.{1 + i}/25'
            self.addHost(f'hB{i}', ip=ip, defaultRoute='via 20.10.172.1')
            self.addLink(f'hB{i}', s2)

        # LAN C: 20.10.172.192/27
        for i in range(1, 3):
            ip = f'20.10.172.{192 + i}/27'
            self.addHost(f'hC{i}', ip=ip, defaultRoute='via 20.10.172.193')
            self.addLink(f'hC{i}', s3)

        # Connect routers to their LAN switches
        self.addLink(rA, s1, intfName1='rA-eth0')  # LAN A
        self.addLink(rB, s2, intfName1='rB-eth0')  # LAN B
        self.addLink(rC, s3, intfName1='rC-eth0')  # LAN C

        # Inter-router links (on 20.10.100.0/24)
        self.addLink(rA, rB, intfName1='rA-eth1', intfName2='rB-eth1')
        self.addLink(rB, rC, intfName1='rB-eth2', intfName2='rC-eth1')
        self.addLink(rA, rC, intfName1='rA-eth2', intfName2='rC-eth2')


def run():
    topo = CustomLAN()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()

    # Assign IPs to router interfaces
    rA, rB, rC = net.get('rA', 'rB', 'rC')

    # LAN interfaces
    rA.setIP('20.10.172.129/26', intf='rA-eth0')
    rB.setIP('20.10.172.1/25', intf='rB-eth0')
    rC.setIP('20.10.172.193/27', intf='rC-eth0')

    # Inter-router interfaces
    rA.setIP('20.10.100.1/24', intf='rA-eth1')  # to B
    rB.setIP('20.10.100.2/24', intf='rB-eth1')  # to A

    rB.setIP('20.10.100.3/24', intf='rB-eth2')  # to C
    rC.setIP('20.10.100.4/24', intf='rC-eth1')  # to B

    rA.setIP('20.10.100.5/24', intf='rA-eth2')  # to C
    rC.setIP('20.10.100.6/24', intf='rC-eth2')  # to A

    # Set routes between routers
    rA.cmd('ip route add 20.10.172.0/25 via 20.10.100.2')     # To LAN B via rB
    rA.cmd('ip route add 20.10.172.192/27 via 20.10.100.6')   # To LAN C via rC

    rB.cmd('ip route add 20.10.172.128/26 via 20.10.100.1')   # To LAN A via rA
    rB.cmd('ip route add 20.10.172.192/27 via 20.10.100.4')   # To LAN C via rC

    rC.cmd('ip route add 20.10.172.128/26 via 20.10.100.5')   # To LAN A via rA
    rC.cmd('ip route add 20.10.172.0/25 via 20.10.100.3')     # To LAN B via rB

    # Test
    print("\n=== Test Intra-LAN Connectivity ===")
    net.ping([net.get('hA1'), net.get('hA2'), net.get('hA3')])
    net.ping([net.get('hB1'), net.get('hB2'), net.get('hB3')])
    net.ping([net.get('hC1'), net.get('hC2')])

    print("\n=== Test Inter-LAN Connectivity ===")
    net.ping([net.get('hA1'), net.get('hB1')])
    net.ping([net.get('hA1'), net.get('hC1')])
    net.ping([net.get('hB2'), net.get('hC2')])

    print("\n=== Traceroute Example ===")
    net.get('hA1').cmd('traceroute 20.10.172.194')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
