from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, Router
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.util import dumpNodeConnections


class MyNetwork(Topo):
    def build(self):
        # Create routers
        rA = self.addNode('rA', cls=Router)
        rB = self.addNode('rB', cls=Router)
        rC = self.addNode('rC', cls=Router)

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

    # Run a simple ping test between hosts on the same LAN
    print("Testing connectivity within LANs")
    net.pingAll()  # Ping all hosts, expect LAN-only communication.

    net.stop()


if __name__ == '__main__':
    runNetwork()
