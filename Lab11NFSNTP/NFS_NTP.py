import subprocess
import socket
import argparse
import distro

distro = distro.name().split(" ")[0]

"""
chronyc -N 'sources -a -v'
"""

def install_services():
    if distro == "Debian":
        subprocess.run(['sudo', 'apt-get', 'update', '-y'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'systemd-timesyncd'], check=True)
        subprocess.run(['systemctl', 'start', 'systemd-timesyncd'])
        subprocess.run(['systemctl', 'enable', 'systemd-timesyncd'])
        print(f"Installed systemd-timesyncd on {distro} machine {socket.gethostname().split('.')[0]}")
    else:
        subprocess.run(['sudo', 'yum', 'update', '-y'], check=True)
        subprocess.run(['yum', '-y', 'install', 'chrony'], check=True)
        subprocess.run(['systemctl', 'start', 'reschronyd'])
        subprocess.run(['systemctl', 'enable', 'chronyd'])
        print(f"Installed chrony on {distro} machine {socket.gethostname().split('.')[0]}")

    if socket.gethostname().split('.')[0] == "nfs":
        subprocess.run(['yum', '-y', 'install', 'nfs-utils'], check=True)
        subprocess.run(['systemctl', 'start', 'nfs-server'])
        subprocess.run(['systemctl', 'enable', 'nfs-server'])
        print(f"Installed nfs-server on {distro} machine {socket.gethostname().split('.')[0]}")
    elif socket.gethostname().split('.')[0] == "web0":
        subprocess.run(['apt-get', 'install', '-y', 'autofs'], check=True)
        subprocess.run(['apt-get', 'install', '-y', 'nfs-common'], check=True)
        print(f"Installed nfs-client on {distro} machine {socket.gethostname().split('.')[0]}")
    elif socket.gethostname().split('.')[0] == "web1":
        subprocess.run(['yum', '-y', 'install', 'autofs'], check=True)
        subprocess.run(['yum', '-y', 'install', 'nfs-utils'], check=True)



def configure_ntp_server():
    if socket.gethostname().split('.')[0] == "router":
        ntp_lines = '''allow 100.64.21.0/24
allow 10.21.32.0/24'''

        with open("/etc/chrony.conf", "r") as chrony_file:
            lines = chrony_file.readlines()

        if ntp_lines not in lines:
            lines.append("\n")
            lines.append(ntp_lines)

        with open("/etc/chrony.conf", "w") as f:
            f.writelines(lines)

        subprocess.run(['systemctl', 'restart', 'chronyd'])
        print(f"Configured NTP Server on distro {distro} Machine {socket.gethostname().split('.')[0]}")

        with open('/etc/dhcp/dhcpd.conf', 'r') as dhcp_conf_file:
            dhcp_lines = dhcp_conf_file.readlines()

        for i, line in enumerate(dhcp_lines):
            if line.strip().startswith("option ntp-servers"):
                dhcp_lines[i] = ""
                with open("/etc/dhcp/dhcpd.conf", "w") as f:
                    f.writelines(dhcp_lines)
                break

        subprocess.run(['systemctl', 'restart', 'dhcpd'], check=True)
        print("Modified dhcpd")

        print(
            f"Configured NTP Server on distro {distro} Machine {socket.gethostname().split('.')[0]} to include Machine A as server")
    else:
        print("Cannot configure this machine as NTP Server")


def configure_ntp_clients():
    if distro == "Debian":
        with open("/etc/systemd/timesyncd.conf", "r") as timesync_file:
            lines = timesync_file.readlines()

        for i, line in enumerate(lines):
            if line.strip().startswith("#NTP=") or line.strip().startswith("NTP="):
                lines[i] = "NTP=100.64.9.1\n"
                with open("/etc/systemd/timesyncd.conf", "w") as f:
                    f.writelines(lines)
                break
        subprocess.run(['systemctl', 'restart', 'systemd-timesyncd'])
        print(f"Configured NTP client on distro {distro} Machine {socket.gethostname().split('.')[0]}")
    else:
        with open("/etc/chrony.conf", "r") as chrony_file:
            lines = chrony_file.readlines()

        if socket.gethostname().split('.')[0] == "nfs":
            new_line = "server 10.21.32.1 iburst prefer"
        else:
            new_line = "server 100.64.9.1 iburst prefer"

        if new_line not in lines:
            lines.append(new_line)

        with open("/etc/chrony.conf", "w") as f:
            f.writelines(lines)

        subprocess.run(['systemctl', 'restart', 'chronyd'])
        print(f"Configured NTP client on distro {distro} Machine {socket.gethostname().split('.')[0]}")


def configure_nfs_server():
    if socket.gethostname().split('.')[0] == "nfs":
        server_directory = "/home/accounting/www"
        subprocess.run(["mkdir", "-p", server_directory], check=True)
        print(f"Created {server_directory} on distro {distro} Machine {socket.gethostname().split('.')[0]}")

        subprocess.run(["chmod", "-R", "2770", server_directory], check=True)
        subprocess.run(["chown", "-R", f":accounting", server_directory], check=True)
        print(
            f"Changed Permissions and Ownership of {server_directory} on distro {distro} Machine {socket.gethostname().split('.')[0]}")

        with open("/etc/exports", "w") as f:
            f.write(f"{server_directory} 100.64.9.0/24 (rw,sync,root_squash,no_all_squash)")
        print(f"Configured NFS export on on distro {distro} Machine {socket.gethostname().split('.')[0]}")

        subprocess.run(['exportfs', '-rav'], check=True)
        subprocess.run(['systemctl', 'restart', 'nfs-server'], check=True)

        print("Refreshed NFS exports and restarted NFS-Server")
    else:
        print("Cannot configure this machine as NFS Server")


def configure_nfs_client():
    if socket.gethostname().split('.')[0] == "web0":
        server_directory = "/home/accounting/www"
        client_directory = "/var/www/html/dundermifflin/accounting"
        subprocess.run(["mkdir", "-p", client_directory], check=True)

        if distro == "Debian":
            subprocess.run(['usermod', '-aG', "accounting", "www-data"])
        else:
            subprocess.run(['usermod', '-aG', "accounting", "apache"])
        # On Machine D: subprocess.run(['usermod', '-aG', "dundermfflinusers", "apache"])
        print(f"Created {client_directory} on distro {distro} Machine {socket.gethostname().split('.')[0]}")

        subprocess.run(
            ["mount", "-t", "nfs", "-o", "ro,soft", f"10.21.32.2:{server_directory}",
             f"{client_directory}"],
            check=True)

        fstab_entries = [
            f"10.21.32.2:{server_directory} {client_directory} nfs ro,soft 0 0\n"
        ]

        with open('/etc/fstab', 'a') as fstab_file:
            for line in fstab_entries:
                fstab_file.write(line)
                print(f"Added entry {line} to /etc/fstab")
    else:
        print("Cannot configure this machine as NFS Client")


def configure_auto_mount():
    server_directory = "/home/accounting/www"
    client_directory = "/var/www/html/dundermifflin/accounting"

    new_line = f"/- /etc/auto.accounting --timeout=60\n"

    with open("/etc/auto.master", "r") as f:
        existing_lines = f.readlines()

    if new_line not in existing_lines:
        with open("/etc/auto.master", "a") as f:
            f.write(new_line)

        with open("/etc/auto.accounting", "w") as f:
            f.write(f"{client_directory} -fstype=nfs4,ro,soft 10.21.32.2:{server_directory}\n")

        print("Configured NFS Auto mount")
        subprocess.run(['systemctl', 'restart', 'autofs'], check=True)
    else:
        print("Entry already exists in /etc/auto.master. No changes made.")

    if distro == "Debian":
        subprocess.run(['usermod', '-aG', "accounting", "www-data"])
    else:
        subprocess.run(['usermod', '-aG', "accounting", "apache"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install NFS and NTP packages")
    parser.add_argument("--ntpserver", action="store_true", help="Configure Machine A as NTP server")
    parser.add_argument("--nfsserver", action="store_true", help="Configure Machine E as NFS server")
    parser.add_argument("--ntpclients", action="store_true", help="Configure Redhat and Debian NTP clients")
    parser.add_argument("--nfsclient", action="store_true", help="Configure Machine C as NFS Client")
    parser.add_argument("--automount", action="store_true", help="Configure Automoung on Machine C and D")
    args = parser.parse_args()

    if args.install:
        install_services()
    elif args.ntpserver:
        configure_ntp_server()
    elif args.ntpclients:
        configure_ntp_clients()
    elif args.nfsserver:
        configure_nfs_server()
    elif args.nfsclient:
        configure_nfs_client()
    elif args.automount:
        configure_auto_mount()
