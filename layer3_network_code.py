from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI


def start():
    """Creates a LAN network with 3 subnets A, B, and C, and connects 3 routers

    Args:
    """

    net = Mininet(controller=Controller, link=TCLink)

    print("*** Adding controller")
    net.addController('c0')

    # Make the switches
    # Use s1 s2 s3 since mininet doesn't support sA etc name scheme
    s1 = net.addSwitch('s1')  # LAN A
    s2 = net.addSwitch('s2')  # LAN B
    s3 = net.addSwitch('s3')  # LAN C

    # Adding routers
    r1 = net.addHost('r1')  # Router 1
    r2 = net.addHost('r2')  # Router 2
    r3 = net.addHost('r3')  # Router 3

    # Hosts
    hB1 = net.addHost('hB1')
    hB2 = net.addHost('hB2')
    hA1 = net.addHost('hA1')
    hA2 = net.addHost('hA2')
    hC1 = net.addHost('hC1')
    hC2 = net.addHost('hC2')

    # Connect routers to switches
    net.addLink(r1, s1)  # eth0 -> LAN A
    net.addLink(r1, s2)  # eth1 -> LAN B
    net.addLink(r2, s2)  # eth0 -> LAN B
    net.addLink(r2, s3)  # eth1 -> LAN C
    net.addLink(r3, s3)  # eth0 -> LAN C
    net.addLink(r3, s1)  # eth1 -> LAN A

    # Connect hosts to switches
    net.addLink(hA1, s1)
    net.addLink(hA2, s1)
    net.addLink(hB1, s2)
    net.addLink(hB2, s2)
    net.addLink(hC1, s3)
    net.addLink(hC2, s3)

    print("*** Starting network")
    net.start()

    print("*** Configuring router interfaces")
    r1.setIP('20.10.100.1/24', intf='r1-eth0')  # Router 1 eth0 -> LAN A
    r1.setIP('20.10.100.2/24', intf='r1-eth1')  # Router 1 eth1 -> LAN B
    r2.setIP('20.10.100.3/24', intf='r2-eth0')  # Router 2 eth0 -> LAN B
    r2.setIP('20.10.100.4/24', intf='r2-eth1')  # Router 2 eth1 -> LAN C
    r3.setIP('20.10.100.5/24', intf='r3-eth0')  # Router 3 eth0 -> LAN C
    r3.setIP('20.10.100.6/24', intf='r3-eth1')  # Router 3 eth1 -> LAN A

    # Set up routing between routers (static routes)
    r1.cmd('ip route add 20.10.100.0/24 via 20.10.100.3')  # Route to r2
    r1.cmd('ip route add 20.10.100.0/24 via 20.10.100.5')  # Route to r3

    r2.cmd('ip route add 20.10.100.0/24 via 20.10.100.1')  # Route to r1
    r2.cmd('ip route add 20.10.100.0/24 via 20.10.100.5')  # Route to r3

    r3.cmd('ip route add 20.10.100.0/24 via 20.10.100.1')  # Route to r1
    r3.cmd('ip route add 20.10.100.0/24 via 20.10.100.3')  # Route to r2

    print("*** Configuring hosts")
    # LAN A
    hA1.setIP('20.10.100.10/24')
    hA2.setIP('20.10.100.11/24')
    hA1.cmd('ip route add default via 20.10.100.1')
    hA2.cmd('ip route add default via 20.10.100.1')

    # LAN B
    hB1.setIP('20.10.100.20/24')
    hB2.setIP('20.10.100.21/24')
    hB1.cmd('ip route add default via 20.10.100.3')
    hB2.cmd('ip route add default via 20.10.100.3')

    # LAN C
    hC1.setIP('20.10.100.30/24')
    hC2.setIP('20.10.100.31/24')
    hC1.cmd('ip route add default via 20.10.100.5')
    hC2.cmd('ip route add default via 20.10.100.5')

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
