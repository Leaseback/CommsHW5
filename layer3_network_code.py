from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel


class CustomTopo(Topo):
    def build(self):
        # Switches for each LAN
        s1 = self.addSwitch('s1')  # LAN B
        s2 = self.addSwitch('s2')  # LAN A
        s3 = self.addSwitch('s3')  # LAN C

        # Router
        router = self.addHost('r1')

        # Hosts in LAN B (/25)
        for i in range(1, 4):
            host = self.addHost(f'hB{i}', ip=f'20.10.172.{i}/25')
            self.addLink(host, s1)
        self.addLink(router, s1)

        # Hosts in LAN A (/26)
        for i in range(1, 4):
            host = self.addHost(f'hA{i}', ip=f'20.10.172.{128 + i}/26')
            self.addLink(host, s2)
        self.addLink(router, s2)

        # Hosts in LAN C (/27)
        for i in range(1, 3):
            host = self.addHost(f'hC{i}', ip=f'20.10.172.{192 + i}/27')
            self.addLink(host, s3)
        self.addLink(router, s3)


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)
    net.start()

    r1 = net.get('r1')

    # Assign IPs to router interfaces manually
    r1.setIP('20.10.172.254/25', intf='r1-eth0')  # LAN B
    r1.setIP('20.10.172.190/26', intf='r1-eth1')  # LAN A
    r1.setIP('20.10.172.222/27', intf='r1-eth2')  # LAN C

    # Enable IP forwarding on router
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Route config on hosts
    def add_routes(host, lan_b_gw, lan_a_gw, lan_c_gw):
        h = net.get(host)
        if host.startswith('hB'):
            h.cmd(f'route add -net 20.10.172.128 netmask 255.255.255.192 gw {lan_b_gw}')
            h.cmd(f'route add -net 20.10.172.192 netmask 255.255.255.224 gw {lan_b_gw}')
        elif host.startswith('hA'):
            h.cmd(f'route add -net 20.10.172.0 netmask 255.255.255.128 gw {lan_a_gw}')
            h.cmd(f'route add -net 20.10.172.192 netmask 255.255.255.224 gw {lan_a_gw}')
        elif host.startswith('hC'):
            h.cmd(f'route add -net 20.10.172.0 netmask 255.255.255.128 gw {lan_c_gw}')
            h.cmd(f'route add -net 20.10.172.128 netmask 255.255.255.192 gw {lan_c_gw}')

    # Add routes to each host
    for host in ['hB1', 'hB2', 'hB3']:
        add_routes(host, '20.10.172.254', '', '')
    for host in ['hA1', 'hA2', 'hA3']:
        add_routes(host, '', '20.10.172.190', '')
    for host in ['hC1', 'hC2']:
        add_routes(host, '', '', '20.10.172.222')

    # Test cross-LAN ping and traceroute
    print("\n=== Cross-LAN Ping Test ===")
    print("hA1 -> hB1:")
    net.get('hA1').cmdPrint('ping -c 2 20.10.172.1')

    print("hC2 -> hA2:")
    net.get('hC2').cmdPrint('ping -c 2 20.10.172.130')

    print("\n=== Cross-LAN Traceroute Test ===")
    print("hA1 -> hB1:")
    net.get('hA1').cmdPrint('traceroute 20.10.172.1')

    print("hB3 -> hC1:")
    net.get('hB3').cmdPrint('traceroute 20.10.172.193')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
