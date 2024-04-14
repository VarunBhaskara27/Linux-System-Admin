import argparse
import subprocess
import os
import shutil
import distro
import getpass


def setup_passwordless_login(user_id, user, target="100.64.9.3", password="theoffice"):
    subprocess.run(['sudo', '-u', user_id, 'ssh-keygen', '-t', 'rsa', '-N', '', '-C', f'{user}'], input="\n", text=True,
                   check=True)
    subprocess.run(['sshpass', '-p', password, 'ssh-copy-id', '-o', 'StrictHostKeyChecking=no', '-i',
                    f'/home/{user_id}/.ssh/id_rsa.pub', f'{user_id}@{target}'], check=True)
    print(f"Created password less login for {user}")


def delete_passwordless_login(user_id, user, target="100.64.9.3"):
    path = os.path.join(f"/home/{user_id}", ".ssh")
    if os.path.exists(path):
        shutil.rmtree(path)
    password = getpass.getpass("Enter password: ")
    subprocess.run(
        ['sshpass', '-p', password, 'ssh', f'{user_id}@{target}', f"sed -i \'/{user}/d\' ~/.ssh/authorized_keys"])
    print(f"Deleted password less login for {user}")


def configure_sudo_all_access(user, sudoers_file):
    with open(sudoers_file, 'w') as file:
        file.write(f"{user} ALL=(ALL:ALL) ALL\n")

    print(f"Granted any command access to user {user}")


def configure_sudo_machine_access(user, sudoers_file, hosts, host_alias, commands, command_alias):
    with open(sudoers_file, 'w') as file:
        file.write(f"{hosts}\n")
        file.write(f"{commands}\n")
        file.write(f"{user} {host_alias}=(ALL:ALL) {command_alias}\n")

    print(f"Granted command access to user {user} on {hosts.split('=')[1]} on commands {commands.split('=')[1]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--createlogin", action="store_true", help="Create password less login for specified users")
    parser.add_argument("--deletelogin", action="store_true", help="Delete password less login for specified users")
    parser.add_argument("--allaccess", action="store_true", help="Grant sudo access to specified user")
    parser.add_argument("--commandaccess", action="store_true",
                        help="Grant sudo access to specified user for a specific command on a specific machine")
    args = parser.parse_args()

    if args.createlogin or args.deletelogin:
        users = ['Kelly Kapoor', 'Pam Beesly', 'Andy Bernard']
        for user in users:
            names = user.split()
            if len(names) > 1:
                user_id = names[0][0].lower() + names[-1].lower()

                if args.deletelogin:
                    delete_passwordless_login(user_id, user, "100.64.9.3")

                if args.createlogin:
                    setup_passwordless_login(user_id, user, "100.64.9.3")
    elif args.allaccess or args.commandaccess:
        distro = distro.name()
        if distro == 'FreeBSD':
            sudoers_file = f"/usr/local/etc/sudoers.d"
        else:
            sudoers_file = f"/etc/sudoers.d"

        if args.allaccess:
            configure_sudo_all_access("dschrute", os.path.join(sudoers_file, "dschrute_config"))

        if args.commandaccess:
            configure_sudo_machine_access("jhalpert", os.path.join(sudoers_file, "jhalpert_config"),
                                          "Host_Alias FILESERVERS = 10.21.32.2", 'FILESERVERS',
                                          'Cmnd_Alias CHANGE_OWNERSHIP_CMDS = /bin/chown [!root]* *',
                                          'CHANGE_OWNERSHIP_CMDS')

            configure_sudo_machine_access("mscott", os.path.join(sudoers_file, "mscott_config"),
                                          "Host_Alias DMZ = 100.64.9.2,100.64.9.3,100.64.9.4,100.64.9.6",
                                          'DMZ',
                                          'Cmnd_Alias SHUTDOWN_CMDS = /sbin/shutdown -h [1-2][2-9][0-9],/sbin/shutdown -h [2-9][0-9][0-9],/sbin/shutdown -c',
                                          'SHUTDOWN_CMDS')
