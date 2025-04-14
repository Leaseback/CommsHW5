from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


class CustomLAN(Topo):
    def build(self):
        # Canonical switch names: s1 = LAN B, s2 = LAN A, s3 = LAN C
        s1 = self.addSwitch('s1')  # LAN B (/25)
        s2 = self.addSwitch('s2')  # LAN A (/26)
        s3 = self.addSwitch('s3')  # LAN C (/27)

        # LAN B: 20.10.172.0/25
        for i in range(1, 4):
            ip = f'20.10.172.{i}/25'
            host = self.addHost(f'hB{i}', ip=ip)
            self.addLink(host, s1)

        # LAN A: 20.10.172.128/26
        for i in range(1, 4):
            ip = f'20.10.172.{128 + i}/26'
            host = self.addHost(f'hA{i}', ip=ip)
            self.addLink(host, s2)

        # LAN C: 20.10.172.192/27
        for i in range(1, 3):
            ip = f'20.10.172.{192 + i}/27'
            host = self.addHost(f'hC{i}', ip=ip)
            self.addLink(host, s3)


def run():
    topo = CustomLAN()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    print("\n=== Testing connectivity within each LAN ===\n")

    print("LAN B:")
    net.ping([net.get('hB1'), net.get('hB2'), net.get('hB3')])

    print("\nLAN A:")
    net.ping([net.get('hA1'), net.get('hA2'), net.get('hA3')])

    print("\nLAN C:")
    net.ping([net.get('hC1'), net.get('hC2')])

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
