import argparse
import subprocess
import distro
import socket

distro = distro.name().split(" ")[0]

"""
named-checkconf
named-checkzone dundermifflin.com /var/named/db.dminternal
named-checkzone 32.21.10.in-addr.arpa /var/named/db.dmreverselan
named-checkzone 9.64.100.in-addr.arpa /var/named/db.dmreversedmz

rndc refresh dundermifflin.com in external
rndc refresh dundermifflin.com in internal
rndc refresh 32.21.10.in-addr.arpa in internal
rndc refresh 9.64.100.in-addr.arpa in external
rndc refresh 9.64.100.in-addr.arpa in internal

named-compilezone -f raw -F text -o dundermifflin.com.txt dundermifflin.com /var/lib/bind/db.dminternal
named-compilezone -f raw -F text -o dundermifflin-ext.com.txt dundermifflin.com /var/lib/bind/db.dmexternal
"""

dmz_reverse = {
    "100.64.9.1": "dmz",
    "100.64.9.2": "dns0",
    "100.64.9.3": "web0",
    "100.64.9.4": "web1",
    "100.64.9.6": "dns1",
    "100.64.9.7": "bsd"
}

dns_servers = {
    "dns0": "100.64.9.2",
    "dns1": "100.64.9.6"
}

lan_reverse = {
    "10.21.32.1": "lan",
    "10.21.32.2": "nfs"
}

router = {
    "100.64.0.9": "router"
}

cname = {
    "100.64.9.1": "machinea",
    "100.64.9.2": "machineb",
    "100.64.9.3": "machinec",
    "100.64.9.4": "machined",
    "100.64.9.6": "machinef",
    "100.64.9.7": "machinex",
    "10.21.32.2": "machinee"
}


def install_packages():
    if distro == "Debian":
        subprocess.run(['apt-get', 'install', '-y', 'dnsutils'], check=True)
    elif distro == "FreeBSD":
        subprocess.run(['pkg', 'install', 'bind-tools'], check=True)
    else:
        subprocess.run(['yum', '-y', 'install', 'bind-utils'], check=True)
    print(f"Installed Dig and NSlookup on machine {socket.gethostname().split('.')[0]}")

    if "dns0" in socket.gethostname().split(".")[0] or "dns1" in socket.gethostname().split(".")[0]:
        if distro == "Rocky":
            subprocess.run(['yum', '-y', 'install', 'bind'], check=True)
            subprocess.run(['systemctl', 'enable', 'named'])
            subprocess.run(['systemctl', 'start', 'named'])
            subprocess.run(['cp', '/etc/named.conf', '/etc/named.conf.orig'])
            print(f"Configured and started named on {distro} {socket.gethostname().split('.')[0]}")
        else:
            subprocess.run(['apt-get', 'install', '-y', 'bind9'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'bind9utils'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'bind9-doc'], check=True)
            subprocess.run(['systemctl', 'restart', 'bind9'])
            subprocess.run(['cp', '/etc/bind/named.conf', '/etc/bind/named.conf.orig'])
            print(f"Configured and started named on {distro} {socket.gethostname().split('.')[0]}")


def create_reverse_db(ip, data):
    db_content = f"$TTL 1h\n"
    db_content += "\n"
    db_content += f"{ip}.in-addr.arpa. IN SOA dns0.dundermifflin.com. vabh4134.colorado.edu. (\n"
    db_content += "    \t\t\t\t20231113   \t\t; serial\n"
    db_content += "    \t\t\t\t1d         \t\t; refresh\n"
    db_content += "    \t\t\t\t1h         \t\t; retry\n"
    db_content += "    \t\t\t\t1w         \t\t; expire\n"
    db_content += "    \t\t\t\t1h)        \t\t; negative cache\n"
    db_content += f"{ip}.in-addr.arpa.\t\t1h\tNS\t\tdns0.dundermifflin.com.\n"
    db_content += f"{ip}.in-addr.arpa.\t\t1h\tNS\t\tdns1.dundermifflin.com.\n"

    for ip, name in data.items():
        parts = ip.split('.')
        reversed_ip = f"{parts[3]}.{parts[2]}.{parts[1]}.{parts[0]}"
        db_content += f"{reversed_ip}.in-addr.arpa.\t1h\tPTR\t\t{name}.dundermifflin.com.\n"

    return db_content


def create_forward_db(type):
    db_content = f"$TTL 1h\n"
    db_content += "$ORIGIN dundermifflin.com.\n"
    db_content += f"@ IN SOA dns0.dundermifflin.com. vabh4134.colorado.edu. (\n"
    db_content += "    \t\t\t\t20231113   \t\t; serial\n"
    db_content += "    \t\t\t\t1d         \t\t; refresh\n"
    db_content += "    \t\t\t\t1h         \t\t; retry\n"
    db_content += "    \t\t\t\t1w         \t\t; expire\n"
    db_content += "    \t\t\t\t1h)        \t\t; negative cache\n"
    db_content += f"@\t\t\t\t1h\tNS\t\tdns0.dundermifflin.com.\n"
    db_content += f"@\t\t\t\t1h\tNS\t\tdns1.dundermifflin.com.\n"

    for ip, name in router.items():
        db_content += f"{name}.dundermifflin.com.\t1h\tA\t\t{ip}\n"

    for ip, name in dmz_reverse.items():
        db_content += f"{name}.dundermifflin.com.\t\t1h\tA\t\t{ip}\n"

    if type == "Internal":
        for ip, name in lan_reverse.items():
            db_content += f"{name}.dundermifflin.com.\t\t1h\tA\t\t{ip}\n"

    # Handling the error in Lab 10 requirements
    db_content += f"dundermifflin.com.\t\t5m\tA\t\t100.64.9.3\n"

    for ip, name in cname.items():
        try:
            if name != "machinea":
                db_content += f"{name}.dundermifflin.com.\t7d\tCNAME\t\t{dmz_reverse[ip]}.dundermifflin.com.\n"
            else:
                db_content += f"{name}.dundermifflin.com.\t7d\tCNAME\t\trouter.dundermifflin.com.\n"
        except KeyError:
            if type == "Internal":
                db_content += f"{name}.dundermifflin.com.\t7d\tCNAME\t\t{lan_reverse[ip]}.dundermifflin.com.\n"

    db_content += f"www.dundermifflin.com.\t\t5m\tCNAME\t\tweb0.dundermifflin.com.\n"
    db_content += f"www1.dundermifflin.com.\t\t5m\tCNAME\t\tweb1.dundermifflin.com.\n"
    db_content += f"dns.dundermifflin.com.\t\t5m\tCNAME\t\tdns0.dundermifflin.com.\n"
    if type == "Internal":
        db_content += f"files.dundermifflin.com.\t7d\tCNAME\t\tnfs.dundermifflin.com.\n"

    return db_content


def run_checkzone(file_path, zone_name):
    command = f"named-checkzone {zone_name} {file_path}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return error.decode()


def configure_primary_dns():
    if socket.gethostname().split(".")[0] == "dns0":
        conf_content = """options {
        listen-on port 53 { 127.0.0.1; 100.64.9.2; };
        directory \"/var/named\";
        allow-query { any; };
        allow-transfer { 100.64.9.6; };
        allow-update { any; };
    };\n\n"""

        conf_content += """logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
    };\n\n"""

        conf_content += """view \"internal\" {
        match-clients { 100.64.9.0/24; 10.21.32.0/24; };
        recursion yes;
    
        zone \"dundermifflin.com\" {
            type primary;
            file "db.dminternal";
        };
    
        zone \"32.21.10.in-addr.arpa\" {
            type primary;
            file "db.dmreverselan";
        };
    
        zone \"9.64.100.in-addr.arpa\" {
            type primary;
            file "db.dmreversedmz";
        };
    
        zone "." IN {
            type hint;
            file "named.ca";
        };
    };\n\n"""

        conf_content += """view \"external\" {
        match-clients { any; };
        recursion no;
    
        zone \"dundermifflin.com\" {
            type primary;
            file "db.dmexternal";
        };
    
        zone \"9.64.100.in-addr.arpa\" {
            type primary;
            file "db.dmreversedmzexternal";
        };
    };\n\n"""

        options_to_add = 'OPTIONS="-4"\n'
        found = False

        with open("/etc/sysconfig/named", "r+") as named_settings:
            lines = named_settings.readlines()
            for line in lines:
                if line == options_to_add:
                    found = True
                    break

            if not found:
                lines.append(options_to_add)
                named_settings.seek(0)
                named_settings.writelines(lines)

        # TODO: Please Refactor!!!!
        with open("/etc/named.conf", "w") as dns_file:
            dns_file.write(conf_content)

        print("Created Named.conf")
        subprocess.run(["chmod", "a+rx", "/etc/named.conf"])

        with open("/var/named/db.dminternal", "w") as internal_db:
            internal_db.write(create_forward_db("Internal"))

        print("Created Internal DNS DB file")

        if run_checkzone("/var/named/db.dminternal", "dundermifflin.com"):
            print(
                f"Errors in file /var/named/db.dminternal please run named-checkzone dundermifflin.com /var/named/db.dminternal to find out more")
            exit(1)
        else:
            subprocess.run(["chmod", "a+rx", "/var/named/db.dminternal"])
            print("No errors")

        with open("/var/named/db.dmexternal", "w") as external_db:
            external_db.write(create_forward_db("External"))

        print("Created External DNS DB file")

        if run_checkzone("/var/named/db.dmexternal", "dundermifflin.com"):
            print(
                f"Errors in file /var/named/db.dmexternal please run named-checkzone dundermifflin.com /var/named/db.dmexternal to find out more")
            exit(1)
        else:
            subprocess.run(["chmod", "a+rx", "/var/named/db.dmexternal"])
            print("No errors")

        with open("/var/named/db.dmreverselan", "w") as lan_file:
            lan_file.write(create_reverse_db("32.21.10", lan_reverse))

        print("Created Internal Lan Reverse DNS DB file")

        if run_checkzone("/var/named/db.dmreverselan", "32.21.10.in-addr.arpa"):
            print(
                f"Errors in file /var/named/db.dmreverselan please run named-checkzone 32.21.10.in-addr.arpa /var/named/db.dmreverselan to find out more")
            exit(1)
        else:
            subprocess.run(["chmod", "a+rx", "/var/named/db.dmreverselan"])
            print("No errors")

        with open("/var/named/db.dmreversedmz", "w") as dmz_file:
            dmz_file.write(create_reverse_db("9.64.100", dmz_reverse))

        print("Created Internal DMZ Reverse DNS DB file")

        if run_checkzone("/var/named/db.dmreversedmz", "9.64.100.in-addr.arpa"):
            print(
                f"Errors in file /var/named/db.dmreversedmz please run named-checkzone 9.64.100.in-addr.arpa /var/named/db.dmreversedmz to find out more")
            exit(1)
        else:
            subprocess.run(["chmod", "a+rx", "/var/named/db.dmreversedmz"])
            print("No errors")

        with open("/var/named/db.dmreversedmzexternal", "w") as dmz_file:
            dmz_file.write(create_reverse_db("9.64.100", dmz_reverse))

        print("Created External DMZ Reverse DNS DB file")

        if run_checkzone("/var/named/db.dmreversedmzexternal", "9.64.100.in-addr.arpa"):
            print(
                f"Errors in file /var/named/db.dminternal please run named-checkzone9.64.100.in-addr.arpa /var/named/db.dmreversedmzexternal to find out more")
            exit(1)
        else:
            subprocess.run(["chmod", "a+rx", "/var/named/db.dmreversedmzexternal"])
            print("No errors")

        subprocess.run(['systemctl', 'restart', 'named'])
        print("Restarted Named Service")
    else:
        print("Not a DNS server")


def configure_secondary_dns():
    if socket.gethostname().split(".")[0] == "dns1":
        conf_content = """options {
        listen-on port 53 { 127.0.0.1; 100.64.9.6; };
        directory \"/var/lib/bind\";
        allow-query { any; };
        allow-update { any; };
};\n\n"""

        conf_content += """view \"internal\" {
        match-clients { 10.21.32.0/24; 100.64.9.0/24; };
        recursion yes;
            
        include "/etc/bind/named.conf.default-zones";
    
        zone \"dundermifflin.com\" {
            type secondary;
            file "db.dminternal";
            masters { 100.64.9.2; };
        };
    
        zone \"32.21.10.in-addr.arpa\" {
            type secondary;
            file "db.dmreverselan";
            masters { 100.64.9.2; };
        };
    
        zone \"9.64.100.in-addr.arpa\" {
            type secondary;
            file "db.dmreversedmz";
            masters { 100.64.9.2; };
        };
};\n\n"""

        conf_content += """view \"external\" {
        match-clients { any; };
        recursion no;
    
        zone \"dundermifflin.com\" {
            type secondary;
            file "db.dmexternal";
            masters { 100.64.9.2; };
        };
    
        zone \"9.64.100.in-addr.arpa\" {
            type secondary;
            file "db.dmreversedmzexternal";
            masters { 100.64.9.2; };
        };
};\n\n"""

        with open("/etc/bind/named.conf", "w") as dns_file:
            dns_file.write(conf_content)

        print("Created Named.conf")

        command = f"named-checkconf"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if not error:
            subprocess.run(['systemctl', 'restart', 'bind9'])
        print("Restarted Named Service")
    else:
        print("Not a secondary DNS server")


def modify_dhcp_dns():
    if socket.gethostname().split(".")[0] == "router":
        new_dns = 'option domain-name-servers 100.64.9.2, 100.64.9.6;\n'
        old_dns = 'option domain-name-servers 128.138.240.1, 128.138.130.30;\n'
        # Modifying DHCP Server config from  128.138.240.1, 128.138.130.30 to 100.64.9.2, 100.64.9.6

        with open("/etc/dhcp/dhcpd.conf", "r") as dhcp_conf:
            lines = dhcp_conf.readlines()

        with open("/etc/dhcp/dhcpd.conf", "w") as dhcp_conf:
            for i in range(len(lines)):
                if lines[i] == old_dns:
                    lines[i] = new_dns
                    dhcp_conf.writelines(lines)
                    print("Added new primary and secondary DNS servers to DHCP server")
                    break
            else:
                dhcp_conf.writelines(lines)

        subprocess.run(['systemctl', 'enable', 'dhcpd'])
        subprocess.run(['systemctl', 'start', 'dhcpd'])
        print("Configured and started DHCP server")

        dns_servers_a = "100.64.9.2, 100.64.9.6"
        for interface in ('ens224', 'ens256'):
            subprocess.run(['nmcli', 'connection', 'modify', interface, 'ipv4.dns', dns_servers_a])
            print(f"Added DNS search and DNS for interface {interface}")
    else:
        print("Not a DHCP server!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install DNS tool packages")
    parser.add_argument("--primary", action="store_true", help="Setup primary DNS server config")
    parser.add_argument("--secondary", action="store_true", help="Setup secondary DNS server config")
    parser.add_argument("--adddns", action="store_true", help="Setup secondary DNS server config")
    args = parser.parse_args()

    if args.install:
        install_packages()
    elif args.primary:
        configure_primary_dns()
    elif args.secondary:
        configure_secondary_dns()
    elif args.adddns:
        modify_dhcp_dns()
