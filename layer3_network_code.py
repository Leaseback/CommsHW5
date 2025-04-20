from mininet.net import Mininet
from mininet.node import Host
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.link import TCLink


class Layer3Topo(Topo):
    def build(self):
        # Create routers (hosts with multiple interfaces)
        routerA = self.addNode('A', cls=Host)
        routerB = self.addNode('B', cls=Host)
        routerC = self.addNode('C', cls=Host)

        # Create hosts for each LAN
        hostA1 = self.addHost('A1')
        hostA2 = self.addHost('A2')
        hostB1 = self.addHost('B1')
        hostB2 = self.addHost('B2')
        hostC1 = self.addHost('C1')
        hostC2 = self.addHost('C2')

        # Add links between routers and hosts
        # LAN A
        self.addLink(hostA1, routerA, intfName="A1-eth0", params={"ip": "20.10.172.1/26"})
        self.addLink(hostA2, routerA, intfName="A2-eth0", params={"ip": "20.10.172.2/26"})

        # LAN B
        self.addLink(hostB1, routerB, intfName="B1-eth0", params={"ip": "20.10.172.65/25"})
        self.addLink(hostB2, routerB, intfName="B2-eth0", params={"ip": "20.10.172.66/25"})

        # LAN C
        self.addLink(hostC1, routerC, intfName="C1-eth0", params={"ip": "20.10.172.129/27"})
        self.addLink(hostC2, routerC, intfName="C2-eth0", params={"ip": "20.10.172.130/27"})

        # Links between routers (inter-router links)
        self.addLink(routerA, routerB, intfName="A-B", params={"ip": "20.10.100.1/24"})
        self.addLink(routerB, routerC, intfName="B-C", params={"ip": "20.10.100.2/24"})
        self.addLink(routerA, routerC, intfName="A-C", params={"ip": "20.10.100.3/24"})


def run():
    # Create the network from the topology
    topo = Layer3Topo()
    net = Mininet(topo=topo, link=TCLink)

    # Start the network
    net.start()

    # Get the routers (hosts)
    routerA = net.get('A')
    routerB = net.get('B')
    routerC = net.get('C')

    # Enable IP forwarding on the routers (hosts)
    routerA.cmd('sysctl -w net.ipv4.ip_forward=1')
    routerB.cmd('sysctl -w net.ipv4.ip_forward=1')
    routerC.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Add static routes on the routers (hosts acting as routers)
    routerA.cmd("ip route add 20.10.172.64/25 dev A-B")  # To LAN B
    routerA.cmd("ip route add 20.10.172.128/27 dev A-C")  # To LAN C
    routerB.cmd("ip route add 20.10.172.0/26 dev A-B")  # To LAN A
    routerB.cmd("ip route add 20.10.172.128/27 dev B-C")  # To LAN C
    routerC.cmd("ip route add 20.10.172.0/26 dev A-C")  # To LAN A
    routerC.cmd("ip route add 20.10.172.64/25 dev B-C")  # To LAN B

    # Test reachability (ping all within the same LAN)
    print("\nTesting connectivity within the same LAN (pingall)...")
    net.pingAll()

    # Start the Mininet CLI
    CLI(net)

    # Stop the network
    net.stop()


if __name__ == "__main__":
    run()
