import argparse
import distro
import socket
import subprocess

distro = distro.name().split(" ")[0]
machine = socket.gethostname().split('.')[0]


def apply_firewall():
    subprocess.run(['systemctl', 'start', 'nftables'])
    subprocess.run(['systemctl', 'enable', 'nftables'])

    firewall_rules = f'''#!/usr/sbin/nft -f

flush ruleset

table ip saclass {{
    # Incoming chain
    chain incoming {{
        #  Default drop
        type filter hook input priority 0; policy drop;
        #  accept loopback
        iifname lo accept
        #  established connections
        ct state invalid drop
        ct state related,established accept
        #  ping
        icmp type {{echo-reply,destination-unreachable,echo-request,time-exceeded}} accept
        #  saclass grader and proxy
        tcp dport {{4113,4114}} accept
        #  ssh from LAN, WAN, DMZ and VPN
        ip saddr {{10.21.32.0/24,100.64.0.0/24,100.64.9.0/24,198.11.0.0/16}} tcp dport 22 accept
        # Allow DNS requests for DNS1 and DNS2
        {"udp dport 53 accept" if machine in ("dns0", "dns1") else ""}
        # Allow incoming DNS requests for dns1 (Machine F)
        {"tcp dport 53 accept" if machine == "dns0" else ""}
        # Prevent zone transfers for dns1
        {"tcp dport 53 reject" if machine == "dns1" else ""}
        # Allow incoming NFS from DMZ
        {"ip saddr 100.64.9.0/24 tcp dport 2049 accept" if machine == "nfs" else ""}
        # Allow incoming http and https for web0 and web1
        {"tcp dport {80,443} accept" if machine in ("web0", "web1") else ""}
    }}

    #  Outgoing chain
    chain outgoing {{
    #  established connections
        #  Default accept except for Machine C and D
        {"type filter hook output priority 0; policy accept;" if machine in ("dns0", "dns1", "nfs") else "type filter hook output priority 0; policy drop;"}
        #  accept loopback
        {"iifname lo accept" if machine in ("web0", "web1") else ""}
        #  established connections
        {"ct state invalid drop" if machine in ("web0", "web1") else ""}
        {"ct state related,established accept" if machine in ("web0", "web1") else ""}
        # Allow outgoing DHCP and NTP to Machine A's DMZ interface
        {"ip daddr {100.64.9.1} udp dport {67, 123} accept" if machine in ("web0", "web1") else ""}
        # Allow outgoing DNS to Machines B and F
        {"ip daddr {100.64.9.2,100.64.9.6} udp dport 53 accept" if machine in ("web0", "web1") else ""}
         # Allow NFS to Machine E
        {"ip daddr {10.21.32.2} tcp dport 2049 accept" if machine in ("web0", "web1") else ""}
        # Allow ssh to only the DMZ subnet.
        {"ip daddr {100.64.9.0/24} tcp dport 22 accept" if machine in ("web0", "web1") else ""}
        # Allow ping to all except the LAN subnet.
        {"ip daddr != 10.21.32.0/24 icmp type echo-request accept" if machine in ("web0", "web1") else ""}
        #  Block facebook
        ip daddr 157.240.28.35 drop
        # Allow http/https to anywhere (for apt and dnf)
        {"tcp dport {80,443} accept" if machine in ("web0", "web1") else ""}
    }}
}}'''

    with open("nftables.conf", "w") as file:
        file.write(firewall_rules)


def all_good():
    if distro == "Rocky":
        target_path = "/etc/sysconfig/nftables.conf"
    else:
        target_path = "/etc/nftables.conf"

    subprocess.run(["mv", "nftables.conf", target_path])
    subprocess.run(["nft", "-f", target_path])
    print("Moved NFTables file and applied ruleset")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Firewall rules for all machines")
    parser.add_argument("--allgood", action="store_true", help="Appy Firewall rules for all machines")
    args = parser.parse_args()

    if args.all:
        apply_firewall()
    elif args.allgood:
        all_good()