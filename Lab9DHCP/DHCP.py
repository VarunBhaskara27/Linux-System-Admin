import argparse
import subprocess
import distro
import socket

distro = distro.name().split(" ")[0]

"""
Debian:
journalctl | grep -i 'dhclient'
systemctl status systemd-timesyncd
ip a
ip r
hostname
cat /etc/resolv.conf

Rocky Linux:
cat /var/log/messages | grep -i 'dhcpd'
chronyc -N 'sources -a -v'
ip a
ip r
hostname
cat /etc/resolv.conf
"""

hosts = {
    "machineb": "100.64.9.2",
    "machinec": "100.64.9.3",
    "machined": "100.64.9.4",
    "machinee": "10.21.32.2",
    "machinef": "100.64.9.6",
}


def install_and_configure():
    subprocess.run(['yum', '-y', 'install', 'dhcp-server'], check=True)
    print("Installed DHCP server")

    dhcp_settings = '''option domain-name "dundermifflin.com";
option domain-name-servers 128.138.240.1, 128.138.130.30;
option ntp-servers time-a-wwv.nist.gov, time-a-b.nist.gov;

default-lease-time 600;
max-lease-time 600;

ping-check true;
ping-timeout-ms 100;
abandon-lease-time 600;

subnet 10.21.32.0 netmask 255.255.255.0 {
    option routers 10.21.32.1;
    range 10.21.32.100 10.21.32.199;
    host machinee {
        hardware ethernet 00:50:56:89:4e:48;
        fixed-address 10.21.32.2;
        option host-name "nfs.dundermifflin.com";
    }
}

subnet 100.64.9.0 netmask 255.255.255.0 {
    option routers 100.64.9.1;
    range 100.64.9.100 100.64.9.199;
    host machineb {
        hardware ethernet 00:50:56:89:8c:45;
        fixed-address 100.64.9.2;
        option host-name "dns0.dundermifflin.com";
    }
    
    host machinec {
        hardware ethernet 00:50:56:89:d1:cb;
        fixed-address 100.64.9.3;
        option host-name "web0.dundermifflin.com";
    }
    
    host machined {
        hardware ethernet 00:50:56:89:82:b2;
        fixed-address 100.64.9.4;
        option host-name "web1.dundermifflin.com";
    }
    
    host machinef {
        hardware ethernet 00:50:56:89:b1:c7;
        fixed-address 100.64.9.6;
        option host-name "dns1.dundermifflin.com";
    }
    
    host machinex {
        hardware ethernet 00:50:56:89:51:85;
        fixed-address 100.64.9.7;
        option host-name "bsd.dundermifflin.com";
    }
}
'''
    with open('/etc/dhcp/dhcpd.conf', 'w') as conf_file:
        conf_file.write(dhcp_settings)

    subprocess.run(['systemctl', 'enable', 'dhcpd'])
    subprocess.run(['systemctl', 'start', 'dhcpd'])
    print("Configured and started DHCP server")


def configure_clients():
    if distro == "Rocky":
        subprocess.run(['yum', '-y', 'install', 'dhcp-client'], check=True)
        print("Installed DHCP server")

        host = socket.gethostname().split(".")[0]
        if host != "machinee":
            GATEWAY = "100.64.9.1"
        else:
            GATEWAY = "10.21.32.1"

        interfaces_config = f'''DEVICE=ens192
ONBOOT=true
BOOTPROTO=dhcp
IPADDR={hosts.get(socket.gethostname().split(".")[0])}
PREFIX=24
GATEWAY={GATEWAY}
'''

        with open('/etc/sysconfig/network-scripts/ifcfg-ens192', 'w') as config_file:
            config_file.write(interfaces_config)

        print(f"Added configuration file ifcfg-ens192 on {socket.gethostname().split('.')[0]}")

        with open('/etc/NetworkManager/system-connections/ens192.nmconnection', 'r') as dhcp_conn:
            lines = dhcp_conn.readlines()
        with open('/etc/NetworkManager/system-connections/ens192.nmconnection', 'w') as dhcp_conn:
            for i, line in enumerate(lines):
                if line.strip() == '[ipv4]':
                    lines[i + 2] = "method=auto\n"
                    dhcp_conn.writelines(lines)
                    break
        print("Modified the value to method=auto in ens192.nmconnection file")

        open("/etc/hostname", "w").close()

        print("Cleared contents of /etc/hostname")

        with open('/etc/NetworkManager/NetworkManager.conf', 'r') as dhcp_conn:
            lines = dhcp_conn.readlines()
        with open('/etc/NetworkManager/NetworkManager.conf', 'w') as dhcp_conn:
            for i, line in enumerate(lines):
                if line.strip() == '[main]':
                    lines[i + 1] = "hostname-mode=dhcp\n"
                    dhcp_conn.writelines(lines)
                    break
        print("Modified the value to hostname-mode=dhcp in NetworkManager.conf file")

        with open('/etc/chrony.conf', 'r') as chrony_file:
            content = chrony_file.readlines()

        change_line = "pool 2.rocky.pool.ntp.org iburst"
        for i, line in enumerate(content):
            if line.strip() == change_line:
                content[i] = "#" + change_line + "\n"
                with open('/etc/chrony.conf', "w") as f:
                    f.writelines(content)
                break
        print(f"Modified the value to {change_line} in /etc/chrony.conf file")

        subprocess.run(['nmcli', 'connection', 'reload'])
        subprocess.run(['nmcli', 'connection', 'up', 'ens192'])
        subprocess.run(['systemctl', 'restart', 'chronyd'])
    elif distro == "FreeBSD":
        try:
            rc_conf_path = "/etc/rc.conf"
            with open(rc_conf_path, 'r') as file:
                lines = file.readlines()

            for i in range(len(lines)):
                if lines[i].startswith('hostname='):
                    lines[i] = '# ' + lines[i]

            for i in range(len(lines)):
                if lines[i].startswith('ifconfig_vmx0='):
                    lines[i] = 'ifconfig_vmx0="DHCP"\n'

            for i in range(len(lines)):
                if lines[i].startswith('defaultrouter='):
                    lines[i] = '# ' + lines[i]

            with open(rc_conf_path, 'w') as file:
                file.writelines(lines)

            print(f"hostname is commented, ifconfig_vmx0 changed to DHCP and defaultrouter is also commented")
            subprocess.run(['service', 'netif', 'restart'])
        except Exception as e:
            print(f"Error: {e}")
    else:
        subprocess.run(['apt-get', 'install', '-y', 'isc-dhcp-client'], check=True)
        print("Installed DHCP server")

        with open('/etc/network/interfaces', 'r') as debian_file:
            content = debian_file.read()
        replacement = 'iface ens192 inet static'
        if replacement in content:
            new_content = content.replace(replacement, "iface ens192 inet dhcp")
            with open('/etc/network/interfaces', "w") as f:
                f.write(new_content)
        print(f"Added dhcp configuration in /etc/network/interfaces {socket.gethostname().split('.')[0]}")

        open("/etc/hostname", "w").close()
        print("Cleared contents of /etc/hostname")

        with open('/etc/dhcp/dhclient.conf', 'r') as debian_file:
            content = debian_file.readlines()

        change_line = "send host-name = gethostname();"
        for i, line in enumerate(content):
            if line.strip() == change_line:
                content[i] = "#" + change_line + "\n"
                with open('/etc/dhcp/dhclient.conf', "w") as f:
                    f.writelines(content)
                break
        print(f"Modified the value to {change_line} in /etc/dhcp/dhclient.conf file")

        subprocess.run(['systemctl', 'restart', 'networking'])
        subprocess.run(['systemctl', 'restart', 'systemd-timesyncd.service'])


def set_machinea_config():
    subprocess.run(['hostnamectl', 'set-hostname', 'router.dundermifflin.com'])
    dns_servers = "128.138.240.1,128.138.130.30"
    domain = "dundermifflin.com"
    for interface in ('ens224', 'ens256'):
        subprocess.run(['nmcli', 'connection', 'modify', interface, 'ipv4.dns-search', domain])
        subprocess.run(['nmcli', 'connection', 'modify', interface, 'ipv4.dns', dns_servers])
        print(f"Added DNS search and DNS for interface {interface}")

    ntp_lines = '''server time-a-wwv.nist.gov iburst
server time-a-b.nist.gov iburst
    '''

    with open("/etc/chrony.conf", "r") as chrony_file:
        lines = chrony_file.readlines()

    new_lines = []

    for line in lines:
        if line.startswith("pool 2.rocky.pool.ntp.org iburst"):
            new_lines.append("# " + line)
        else:
            new_lines.append(line)

    for line in new_lines:
        if line.startswith("# pool 2.rocky.pool.ntp.org iburst"):
            new_lines.append(ntp_lines)

    with open("/etc/chrony.conf", "w") as chrony_file:
        chrony_file.writelines(new_lines)

    subprocess.run(['systemctl', 'restart', 'chronyd'])
    print("Added config for NTP into Machine A")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true", help="Install DHCP and configure")
    parser.add_argument("--clients", action="store_true", help="Install DHCP and configure on clients")
    parser.add_argument("--static", action="store_true", help="Set static config for Machine A")
    args = parser.parse_args()

    if args.server:
        install_and_configure()
    elif args.clients:
        configure_clients()
    elif args.static:
        set_machinea_config()
