import argparse
import subprocess
import os
import shutil
import distro
import getpass

distro = distro.name().split(" ")[0]

host_ip = {
    "machinea": "100.64.9.1",
    "machineb": "100.64.9.2",
    "machinec": "100.64.9.3",
    "machined": "100.64.9.4",
    "machinef": "100.64.9.6"
}

web_servers = {
    "machinec": "100.64.9.3",
    "machined": "100.64.9.4"
}


# host_ip = {
#     "machinea": "10.0.2.4"
# }


def install_ansible(machine):
    subprocess.run(['sudo', 'yum', 'update'], check=True)
    subprocess.run(['sudo', 'yum', '-y', 'install', 'epel-release'], check=True)
    subprocess.run(['sudo', 'yum', '-y', 'install', 'ansible'], check=True)
    print(f"Installed Ansible on machine {machine}")


def setup_passwordless_login(user_id, password="theoffice"):
    subprocess.run(['sudo', '-u', user_id, 'ssh-keygen', '-t', 'rsa', '-N', '', '-C', user_id], input="\n", text=True,
                   check=True)
    for key, value in host_ip.items():
        subprocess.run(
            ['sshpass', '-p', password, 'ssh', f'{user_id}@{value}', f"sed -i \'/{user_id}/d\' ~/.ssh/authorized_keys"])
        subprocess.run(['sshpass', '-p', password, 'ssh-copy-id', '-i',
                        f'/home/{user_id}/.ssh/id_rsa.pub', f'{user_id}@{value}'], check=True)
        print(f"Created password less login for {user_id} on {key}")


def delete_passwordless_login(user_id):
    path = os.path.join(f"/home/{user_id}", ".ssh")
    if os.path.exists(path):
        shutil.rmtree(path)
    print(f"Deleted password less login for {user_id}")


def configure_ansible():
    ansible_dir = "/etc/ansible"
    cfg_file = os.path.join(ansible_dir, "ansible.cfg")
    hosts_file = os.path.join(ansible_dir, "hosts")
    os.remove(cfg_file) if os.path.exists(cfg_file) else None
    with open(cfg_file, "w") as f:
        subprocess.run(['sudo', 'ansible-config', 'init', '--disabled', '-t', 'all'], stdout=f, check=True)
    with open(cfg_file, "r") as f:
        lines = f.readlines()
    for i in range(len(lines)-1, -1, -1):
        if lines[i].startswith(";pipelining=False"):
            lines[i + 1] = "pipelining=True\n"
            with open(cfg_file, "w") as f2:
                f2.writelines(lines)
            print(f"Added pipelining to ssh_connections")
            break
    else:
        print(f"Config file already has pipelining in ssh_connections")

    print("Created config file and enabled pipelining")

    os.remove(hosts_file) if os.path.exists(hosts_file) else None

    with open(hosts_file, "a") as h:
        for key, value in host_ip.items():
            h.writelines(f"{key} ansible_host={value} ansible_ssh_user={os.getenv('SUDO_USER', getpass.getuser())} ansible_ssh_private_key_file=/home/{os.getenv('SUDO_USER', getpass.getuser())}/.ssh/id_rsa\n")

    with open(hosts_file, "a") as h:
        h.writelines("\n[saclass]\n")
        for val in host_ip.keys():
            h.writelines(f"{val}\n")
        h.writelines("\n[webservers]\n")
        for val in web_servers.keys():
            h.writelines(f"{val}\n")

    print("Created hosts file with saclass config")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--createlogin", action="store_true", help="Create password less login for specified users")
    parser.add_argument("--configure", action="store_true", help="Configure Ansible files and setup hosts")
    args = parser.parse_args()

    if args.createlogin:
        install_ansible(distro)
        delete_passwordless_login("vabh4134")
        setup_passwordless_login("vabh4134")
    elif args.configure:
        configure_ansible()
