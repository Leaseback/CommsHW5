from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        # Ensure interfaces are up
        self.cmd('ifconfig rA-eth1 up')
        self.cmd('ifconfig rA-eth2 up')
        self.cmd('ifconfig rB-eth1 up')
        self.cmd('ifconfig rB-eth2 up')
        self.cmd('ifconfig rC-eth1 up')
        self.cmd('ifconfig rC-eth2 up')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


class CustomLAN(Topo):
    def build(self):
        # Routers
        rA = self.addNode('rA', cls=LinuxRouter, ip='20.10.172.129/26')
        rB = self.addNode('rB', cls=LinuxRouter, ip='20.10.172.1/25')
        rC = self.addNode('rC', cls=LinuxRouter, ip='20.10.172.193/27')

        # Switches for each LAN
        s1 = self.addSwitch('s1')  # LAN B
        s2 = self.addSwitch('s2')  # LAN A
        s3 = self.addSwitch('s3')  # LAN C

        # Connect routers to their switches (LANs)
        self.addLink(rB, s1)  # Router B to LAN B
        self.addLink(rA, s2)  # Router A to LAN A
        self.addLink(rC, s3)  # Router C to LAN C

        # Hosts in LAN B (/25)
        for i in range(1, 4):
            ip = f'20.10.172.{i + 1}/25'
            host = self.addHost(f'hB{i}', ip=ip, defaultRoute='via 20.10.172.1')
            self.addLink(host, s1)

        # Hosts in LAN A (/26)
        for i in range(1, 4):
            ip = f'20.10.172.{128 + i}/26'
            host = self.addHost(f'hA{i}', ip=ip, defaultRoute='via 20.10.172.129')
            self.addLink(host, s2)

        # Hosts in LAN C (/27)
        for i in range(1, 3):
            ip = f'20.10.172.{192 + i}/27'
            host = self.addHost(f'hC{i}', ip=ip, defaultRoute='via 20.10.172.193')
            self.addLink(host, s3)

        # Inter-router links (20.10.100.0/24)
        self.addLink(rA, rB, intfName1='rA-eth1', intfName2='rB-eth1', params1={'ip': '20.10.100.1/24'}, params2={'ip': '20.10.100.2/24'})
        self.addLink(rB, rC, intfName1='rB-eth2', intfName2='rC-eth1', params1={'ip': '20.10.100.3/24'}, params2={'ip': '20.10.100.4/24'})
        self.addLink(rC, rA, intfName1='rC-eth2', intfName2='rA-eth2', params1={'ip': '20.10.100.5/24'}, params2={'ip': '20.10.100.6/24'})


def run():
    topo = CustomLAN()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()

    # Set static routes for inter-router communication
    rA, rB, rC = net.get('rA'), net.get('rB'), net.get('rC')

    # Routes for rA
    rA.cmd('ip route add 20.10.172.0/25 via 20.10.100.2')
    rA.cmd('ip route add 20.10.172.192/27 via 20.10.100.5')

    # Routes for rB
    rB.cmd('ip route add 20.10.172.128/26 via 20.10.100.1')
    rB.cmd('ip route add 20.10.172.192/27 via 20.10.100.4')

    # Routes for rC
    rC.cmd('ip route add 20.10.172.0/25 via 20.10.100.3')
    rC.cmd('ip route add 20.10.172.128/26 via 20.10.100.6')

    # Check if routing is working with ping
    print("\n=== Testing connectivity within each LAN ===\n")
    print("LAN B:")
    net.ping([net.get('hB1'), net.get('hB2'), net.get('hB3')])
    print("\nLAN A:")
    net.ping([net.get('hA1'), net.get('hA2'), net.get('hA3')])
    print("\nLAN C:")
    net.ping([net.get('hC1'), net.get('hC2')])

    # Test inter-LAN pings (ping between hosts in different LANs)
    print("\n=== Testing inter-LAN connectivity ===\n")
    print("Ping from hB1 to hA1:")
    net.ping([net.get('hB1'), net.get('hA1')])
    print("Ping from hA1 to hC1:")
    net.ping([net.get('hA1'), net.get('hC1')])

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
