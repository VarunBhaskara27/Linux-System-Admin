import socket
import subprocess
import paramiko
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

password = ""

machinea_lan = '10.21.32.0'
machinea_dmz = '100.64.9.0'

machinea = '100.64.9.1'
machineb = '100.64.9.2'
machinec = '100.64.9.3'
machined = '100.64.9.4'
machinee = '10.21.32.2'
machinef = '100.64.9.6'


def ping_vm(ip_address):
    try:
        process = subprocess.Popen(["ping", "-w", "1", "-n", "3", ip_address], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        process.wait()

        if process.returncode == 0:
            print(f"{Fore.GREEN}Ping to {ip_address} SUCCESSFUL{Style.RESET_ALL}")

            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh_client.connect(ip, username="root", password=password, timeout=2)
                print(f"{Fore.GREEN}SSH established to {ip_address} {Style.RESET_ALL}")

            except socket.timeout:
                print(f"{Fore.RED}Timeout:1 Unable to establish SSH connection within 2 seconds.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            finally:
                if ssh_client:
                    ssh_client.close()
        else:
            print(f"{Fore.RED}Ping at {ip_address} FAILED{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


def ssh_to_a_and_ping(target_ip):
    # SSH into the VM
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(machinea, username="root", password=password, timeout=2)
        print("SSH connection established to Machine A")

        # Run the ping command on the VM
        ping_command = f'ping -W 1 -c 3 -i 0.1 {target_ip}'
        stdin, stdout, stderr = ssh_client.exec_command(ping_command)

        # Wait for the command to finish
        exit_status = stdout.channel.recv_exit_status()

        # Check if the ping command was successful
        if exit_status == 0:
            print(f"{Fore.GREEN}Ping to {target_ip} from {machinea} was SUCCESSFUL{Style.RESET_ALL}.")

            # Create an SSH tunnel to Machine E through Machine A
            transport = ssh_client.get_transport()
            tunnel = transport.open_channel(
                'direct-tcpip', (target_ip, 22), (machinea, 22)
            )

            # Connect to the target host (Machine E) through the tunnel
            target_client = paramiko.SSHClient()
            target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                target_client.connect(target_ip, username="root", password=password, timeout=2, sock=tunnel)
                print(f"{Fore.GREEN}SSH established to {target_ip} from {machinea} {Style.RESET_ALL}")

            except socket.timeout:
                print(f"{Fore.RED}Timeout:2 Unable to establish SSH connection to {target_ip} from {machinea} within 2 seconds.{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            finally:
                if 'target_client' in locals():
                    target_client.close()
        else:
            print(f"{Fore.RED}Ping to {target_ip} from {machinea} FAILED{Style.RESET_ALL}.")

    except socket.timeout:
        print(f"{Fore.RED}Timeout:3 Unable to establish SSH connection within 2 seconds.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    finally:
        if ssh_client:
            ssh_client.close()


def check_dns(ip_address, domain):
    try:
        cmd = ["dig", "+time=1", "+tries=1", f"@{ip_address}", domain]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.wait()

        output = process.stdout.read().decode('utf-8')
        cname_count = len([line for line in output.split('\n') if line.startswith(f"{domain}.") and "CNAME" in line])

        if cname_count == 1:
            print(f"DNS Server to {ip_address} Successful!")
        else:
            print(f"DNS Server to {ip_address} Failed!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


def check_web(resolve_ip, url, term, cnt, timeout=1):
    try:
        # Run the curl command
        cmd = ["curl", "--silent", "--connect-timeout", str(timeout), "--resolv", f"{url}:80:{resolve_ip}",
               f"http://{url}/index.html"]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        output = process.stdout.read().decode('utf-8')
        count = len([line for line in output.split('\n') if term in line])

        if count == cnt:
            print(f"Web Server to {url} in {resolve_ip} Successful!")
        else:
            print(f"Web Server to {url} in {resolve_ip} Failed!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    # SSH connection details
    machines_and_ips = {
        'A': machinea,
        'B': machineb,
        'C': machinec,
        'D': machined,
        'E': machinee,
        'F': machinef
    }

    # Logs into machine A
    for machine, ip in machines_and_ips.items():
        # check(machine, ip)
        print(f"\n------Machine {machine}---------")
        if machine != 'E':
            ping_vm(ip)

        if machine != 'A':
            ssh_to_a_and_ping(ip)

    domain = "www.dundermifflin.com"
    print("\n------DNS---------")
    check_dns(machineb, domain)
    check_dns(machinef, domain)

    print("\n------WEB---------")
    dundermifflin_domain = "www.dundermifflin.com"
    dundermifflin_accounting_domain = "www.dundermifflin.com/accounting"
    mspc_domain = "www.michaelscottpapercompany.com"
    sf_domain = "www.schrutefarms.com"
    check_web(machinec, dundermifflin_domain, 'scranton', 18)
    # check_web(machinec, dundermifflin_accounting_domain)
    check_web(machinec, mspc_domain, 'scranton', 2)
    check_web(machinec, sf_domain,'Schrute', 17)