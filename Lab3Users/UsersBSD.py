import argparse
import subprocess
import os
import crypt
import random
import string

users = ['Michael Scott', 'Dwight Schrute', 'Jim Halpert', 'Toby Flenderson', 'Creed Bratton', 'Darryl Philbin',
         'Angela Martin', 'Kevin Malone', 'Oscar Martinez',
         'Meredith Palmer', 'Kelly Kapoor', 'Pam Beesly', 'Andy Bernard', 'Phyllis Lapin', 'Stanley Hudson', 'vabh4134']

secondary_group = {'managers': ['mscott', 'dschrute', 'jhalpert'],
                   'sales': ['abernard', 'plapin', 'shudson'],
                   'accounting': ['amartin', 'kmalone', 'omartinez']}

uid_start = 3000


def create_user(username, gecos, uid, home_dir, shell='/usr/local/bin/bash'):
    # Create accounts
    subprocess.run(['pw', 'useradd', '-n', username, '-c', gecos, '-d', home_dir, '-u', str(uid), '-s', shell, '-m'])
    subprocess.run(['chpass', '-p', crypt.crypt("theoffice", ''.join(random.choices(string.ascii_lowercase, k=2))), username])

    # Change ownership
    subprocess.run(['chown', '-R', f'{username}:{username}', home_dir])

    # Set permissions for home
    subprocess.run(['chmod', '700', home_dir])


def create_group(groupname, members):
    # Create a group
    subprocess.run(['pw', 'groupadd', groupname])
    print(f"Created secondary group {groupname}")

    # Add members to group
    for member in members:
        subprocess.run(['pw', 'groupmod', groupname, '-m', member])
        print(f"Added member {member} to secondary group {groupname}")


def delete_user(username):
    # Delete user and their home directory
    subprocess.run(['pw', 'userdel', username, '-r'])
    print(f"Deleted user {username}")


def delete_group(groupname):
    # Delete a group
    subprocess.run(['pw', 'groupdel', groupname])
    print(f"Deleted group {groupname}")


def create_users_and_groups():
    for i, user in enumerate(users):
        uid = uid_start + i
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
        else:
            user_id = user
            user = "Varun Bhaskara"

        shell = '/usr/local/bin/bash'
        home_dir = f'/home/{user_id}'
        create_user(user_id, user, uid, home_dir, shell)
        print(f"Created user {user_id} with UID: {uid}, GID: {uid}, home_dir: {home_dir}, shell: {shell}")

    for group, members in secondary_group.items():
        create_group(group, members)


def delete_users_and_groups():
    for group in secondary_group.keys():
        delete_group(group)

    for user in users:
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
        else:
            user_id = user
        delete_user(user_id)


def set_umask(umask_value="0007"):
    with open("/etc/login.conf", 'r') as file:
        contents = file.read()

    contents = contents.replace(":umask=022:", f":umask={umask_value}:")

    with open("/etc/login.conf", 'w') as file:
        file.write(contents)

    subprocess.run(['cap_mkdb', '/etc/login.conf'])

    os.umask(int(umask_value, 8))

    print(f"Updated umask value to {umask_value}")


def add_sys_admin(username='vabh4134'):
    subprocess.run(['pw', 'groupmod', 'wheel', '-m', username])
    print(f"Added Sys admin user to sudo group {username}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or delete users, home directories, and groups.")
    parser.add_argument("--create", action="store_true", help="Create users, home directories, and groups.")
    parser.add_argument("--delete", action="store_true", help="Delete users, home directories, and groups.")
    parser.add_argument("--umask", action="store_true", help="Set the umask value for new directories.")
    args = parser.parse_args()

    if args.create:
        create_users_and_groups()
        add_sys_admin(users[-1])
    elif args.delete:
        delete_users_and_groups()
    elif args.umask:
        set_umask()
    else:
        print("Please specify either --create or --delete.")
