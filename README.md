# Mininet LAN Routing Simulation

This project sets up a simulated LAN network with **3 subnets (LAN A, B, and C)** and **3 routers** using **Mininet**. Each LAN has 2 hosts and is connected to 2 routers, allowing for inter-subnet communication with manually configured IPs and static routes.

## 🛠 Requirements

- Python 3
- Mininet installed on a Linux machine (typically via a VM or Ubuntu system)

To install Mininet:

```bash
sudo apt-get update
sudo apt-get install mininet
```

## 🚀 How to Run

1. Save the script to a file, e.g., `lan_routing.py`.

2. Run the script with root privileges:

```bash
sudo python3 lan_routing.py
```

3. This will:
   - Start the Mininet simulation
   - Set up 3 LANs, each with 2 hosts
   - Create 3 routers connecting the LANs
   - Assign IP addresses
   - Enable IP forwarding on routers
   - Set static routes on routers and default routes on hosts
   - Drop into the Mininet CLI so you can run tests

4. In the CLI, try pinging between hosts in different LANs to verify routing:

```bash
hA1 ping hB1
hC2 ping hA2
```

5. Exit the CLI with:

```bash
exit
```

## 🧪 Example Usage

Start the network:

```bash
sudo python3 lan_routing.py
```

In the Mininet CLI:

```bash
hA1 ping hC1
hB2 ping hA2
```

Expected output should show successful pings, indicating that routing between LANs works.

## 🧰 Network Topology

```
LAN A (s1): hA1, hA2
  ↕
Router r1 ↔ Router r2 ↔ LAN C (s3): hC1, hC2
  ↕         ↕
LAN B (s2): hB1, hB2
      ↕
Router r3
```

Each router is connected to two LANs, forming a loop-like topology that allows for redundancy in routing paths.

## 📄 Notes

- All devices are manually configured with static IP addresses.
- No dynamic routing protocols are used.
- You can modify the script to simulate link failures or add more subnets for advanced testing.
