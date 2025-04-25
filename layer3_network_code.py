from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI


def start():
    """Creates a LAN network with 3 routers (A, B, C), each connected to two hosts"""

    net = Mininet(controller=Controller, link=TCLink)

    print("*** Adding controller")
    net.addController('c0')

    # Make the switches
    s1 = net.addSwitch('s1')  # LAN A
    s2 = net.addSwitch('s2')  # LAN B
    s3 = net.addSwitch('s3')  # LAN C

    # Adding routers
    r1 = net.addHost('r1')  # Router A
    r2 = net.addHost('r2')  # Router B
    r3 = net.addHost('r3')  # Router C

    # Hosts
    hA1 = net.addHost('hA1')
    hA2 = net.addHost('hA2')
    hB1 = net.addHost('hB1')
    hB2 = net.addHost('hB2')
    hC1 = net.addHost('hC1')
    hC2 = net.addHost('hC2')

    # Connect routers to switches (LANs)
    net.addLink(r1, s1)  # Router A -> LAN A
    net.addLink(r1, s2)  # Router A -> LAN B
    net.addLink(r2, s2)  # Router B -> LAN B
    net.addLink(r2, s3)  # Router B -> LAN C
    net.addLink(r3, s3)  # Router C -> LAN C
    net.addLink(r3, s1)  # Router C -> LAN A

    # Connect hosts to switches (LANs)
    net.addLink(hA1, s1)
    net.addLink(hA2, s1)
    net.addLink(hB1, s2)
    net.addLink(hB2, s2)
    net.addLink(hC1, s3)
    net.addLink(hC2, s3)

    print("*** Starting network")
    net.start()

    print("*** Configuring router interfaces")
    r1.setIP('20.10.100.1/24', intf='r1-eth0')  # Router A <-> Router B
    r1.setIP('20.10.100.2/24', intf='r1-eth1')  # Router A <-> Router C
    r2.setIP('20.10.100.1/24', intf='r2-eth0')  # Router B <-> Router A
    r2.setIP('20.10.100.3/24', intf='r2-eth1')  # Router B <-> Router C
    r3.setIP('20.10.100.2/24', intf='r3-eth0')  # Router C <-> Router A
    r3.setIP('20.10.100.3/24', intf='r3-eth1')  # Router C <-> Router B

    # Configure static routes between routers
    r1.cmd('ip route add 192.168.2.0/24 via 20.10.100.1')  # Route to LAN B via Router B
    r1.cmd('ip route add 192.168.3.0/24 via 20.10.100.2')  # Route to LAN C via Router C

    r2.cmd('ip route add 192.168.1.0/24 via 20.10.100.1')  # Route to LAN A via Router A
    r2.cmd('ip route add 192.168.3.0/24 via 20.10.100.3')  # Route to LAN C via Router C

    r3.cmd('ip route add 192.168.1.0/24 via 20.10.100.2')  # Route to LAN A via Router A
    r3.cmd('ip route add 192.168.2.0/24 via 20.10.100.3')  # Route to LAN B via Router B

    print("*** Configuring hosts IPs")
    # LAN A
    hA1.setIP('192.168.1.10/24')
    hA2.setIP('192.168.1.11/24')
    hA1.cmd('ip route add default via 192.168.1.1')
    hA2.cmd('ip route add default via 192.168.1.1')

    # LAN B
    hB1.setIP('192.168.2.10/24')
    hB2.setIP('192.168.2.11/24')
    hB1.cmd('ip route add default via 192.168.2.1')
    hB2.cmd('ip route add default via 192.168.2.1')

    # LAN C
    hC1.setIP('192.168.3.10/24')
    hC2.setIP('192.168.3.11/24')
    hC1.cmd('ip route add default via 192.168.3.1')
    hC2.cmd('ip route add default via 192.168.3.1')

    print("*** Enabling IP forwarding on routers")
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')
    r3.cmd('sysctl -w net.ipv4.ip_forward=1')

    print("*** Dropping to CLI")
    CLI(net)

    print("*** Stopping network")
    net.stop()


if __name__ == '__main__':
    start()
