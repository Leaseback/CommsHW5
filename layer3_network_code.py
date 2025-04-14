from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


class CustomLAN(Topo):
    def build(self):
        # Add routers
        rA = self.addHost('rA', ip='20.10.172.1/25')  # Router A
        rB = self.addHost('rB', ip='20.10.172.129/26')  # Router B
        rC = self.addHost('rC', ip='20.10.172.193/27')  # Router C

        # Add switches for each LAN
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

        # Connect routers to switches
        self.addLink(rA, s1)  # rA to LAN B
        self.addLink(rA, s2)  # rA to LAN A
        self.addLink(rB, s2)  # rB to LAN A
        self.addLink(rB, s3)  # rB to LAN C
        self.addLink(rC, s3)  # rC to LAN C
        self.addLink(rC, s1)  # rC to LAN B


def run():
    topo = CustomLAN()
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    # Set routes on the routers
    rA = net.get('rA')
    rB = net.get('rB')
    rC = net.get('rC')

    # Add routes on routers
    print("\n=== Setting routes on routers ===")
    rA.cmd('route add -net 20.10.172.0 netmask 255.255.255.128 gw 20.10.172.2')  # Route to LAN B
    rA.cmd('route add -net 20.10.172.192 netmask 255.255.255.224 gw 20.10.172.3')  # Route to LAN C

    rB.cmd('route add -net 20.10.172.0 netmask 255.255.255.128 gw 20.10.172.1')  # Route to LAN B
    rB.cmd('route add -net 20.10.172.192 netmask 255.255.255.224 gw 20.10.172.3')  # Route to LAN C

    rC.cmd('route add -net 20.10.172.0 netmask 255.255.255.128 gw 20.10.172.1')  # Route to LAN B
    rC.cmd('route add -net 20.10.172.128 netmask 255.255.255.192 gw 20.10.172.2')  # Route to LAN A

    # Set routes on the hosts
    print("\n=== Setting routes on hosts ===")
    # LAN A hosts
    for i in range(1, 4):
        host = net.get(f'hA{i}')
        host.cmd(f'route add -net 20.10.172.0 netmask 255.255.255.128 gw 20.10.172.1')  # Gateway to LAN B
        host.cmd(f'route add -net 20.10.172.192 netmask 255.255.255.224 gw 20.10.172.3')  # Gateway to LAN C

    # LAN B hosts
    for i in range(1, 4):
        host = net.get(f'hB{i}')
        host.cmd(f'route add -net 20.10.172.128 netmask 255.255.255.192 gw 20.10.172.2')  # Gateway to LAN A
        host.cmd(f'route add -net 20.10.172.192 netmask 255.255.255.224 gw 20.10.172.3')  # Gateway to LAN C

    # LAN C hosts
    for i in range(1, 3):
        host = net.get(f'hC{i}')
        host.cmd(f'route add -net 20.10.172.0 netmask 255.255.255.128 gw 20.10.172.1')  # Gateway to LAN B
        host.cmd(f'route add -net 20.10.172.128 netmask 255.255.255.192 gw 20.10.172.2')  # Gateway to LAN A

    # Test connectivity within each LAN (Ping)
    print("\n=== Testing connectivity within each LAN ===\n")
    print("LAN B:")
    net.ping([net.get('hB1'), net.get('hB2'), net.get('hB3')])

    print("\nLAN A:")
    net.ping([net.get('hA1'), net.get('hA2'), net.get('hA3')])

    print("\nLAN C:")
    net.ping([net.get('hC1'), net.get('hC2')])

    # Test connectivity across LANs (Ping)
    print("\n=== Testing connectivity across LANs ===\n")
    net.ping([net.get('hA1'), net.get('hB1')])  # Example: Ping between LAN A and LAN B
    net.ping([net.get('hA1'), net.get('hC1')])  # Example: Ping between LAN A and LAN C

    # Test with traceroute
    print("\n=== Traceroute from hA1 to hC1 ===")
    net.get('hA1').cmd('traceroute 20.10.172.193')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
