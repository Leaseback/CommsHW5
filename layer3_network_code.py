from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, Node
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.util import dumpNodeConnections


class MyNetwork(Topo):
    def build(self):
        # Create routers (actually, Hosts acting as routers)
        rA = self.addNode('rA', cls=Node)
        rB = self.addNode('rB', cls=Node)
        rC = self.addNode('rC', cls=Node)

        # Create hosts
        hA1 = self.addHost('hA1')
        hA2 = self.addHost('hA2')
        hB1 = self.addHost('hB1')
        hB2 = self.addHost('hB2')
        hC1 = self.addHost('hC1')
        hC2 = self.addHost('hC2')

        # Connect routers to each other with links
        self.addLink(rA, rB)
        self.addLink(rB, rC)
        self.addLink(rA, rC)

        # Connect routers to hosts
        self.addLink(rA, hA1)
        self.addLink(rA, hA2)
        self.addLink(rB, hB1)
        self.addLink(rB, hB2)
        self.addLink(rC, hC1)
        self.addLink(rC, hC2)


def runNetwork():
    net = Mininet(topo=MyNetwork(), controller=Controller, link=TCLink, switch=OVSKernelSwitch)
    net.start()
    dumpNodeConnections(net.hosts)

    # Enable IP forwarding on all routers (hosts acting as routers)
    rA = net.get('rA')
    rB = net.get('rB')
    rC = net.get('rC')
    rA.cmd('sysctl -w net.ipv4.ip_forward=1')
    rB.cmd('sysctl -w net.ipv4.ip_forward=1')
    rC.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Assign IP addresses to the routers and hosts
    hA1 = net.get('hA1')
    hA2 = net.get('hA2')
    hB1 = net.get('hB1')
    hB2 = net.get('hB2')
    hC1 = net.get('hC1')
    hC2 = net.get('hC2')

    hA1.setIP('20.10.172.129/26')
    hA2.setIP('20.10.172.130/26')
    hB1.setIP('20.10.172.1/25')
    hB2.setIP('20.10.172.2/25')
    hC1.setIP('20.10.172.193/27')
    hC2.setIP('20.10.172.194/27')

    # Test connectivity within LANs
    print("Testing connectivity within LANs")
    net.pingAll()  # Ping all hosts, expect LAN-only communication.

    net.stop()


if __name__ == '__main__':
    runNetwork()
