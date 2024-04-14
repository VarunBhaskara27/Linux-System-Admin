import argparse
import subprocess
import distro
import os
import socket
import glob
import shutil

users = ['Michael Scott', 'Dwight Schrute', 'Jim Halpert', 'Toby Flenderson', 'Creed Bratton', 'Darryl Philbin',
         'Angela Martin', 'Kevin Malone', 'Oscar Martinez',
         'Meredith Palmer', 'Kelly Kapoor', 'Pam Beesly', 'Andy Bernard', 'Phyllis Lapin', 'Stanley Hudson', 'vabh4134']

secondary_group = {'managers': ['mscott', 'dschrute', 'jhalpert'],
                   'sales': ['abernard', 'plapin', 'shudson'],
                   'accounting': ['amartin', 'kmalone', 'omartinez']}

uid_start = 3000



def create_user(username, gecos, uid, home_dir, shell='/bin/bash'):
    # Create accounts
    subprocess.run(['useradd', '-U', '-m', '-d', home_dir, '-c', gecos, '-u', str(uid), '-s', shell, username])

    # Set default password
    subprocess.run(['passwd', username], input='theoffice\ntheoffice\n', universal_newlines=True)

    # Change ownership
    subprocess.run(['chown', '-R', f'{username}:{username}', home_dir])

    # Set permissions for home
    subprocess.run(['chmod', '700', home_dir])


def create_group(groupname, members):
    # Create a group
    subprocess.run(['groupadd', groupname])
    print(f"Created secondary group {groupname}")

    # Add members to group
    for member in members:
        subprocess.run(['usermod', '-aG', groupname, member])
        print(f"Added member {member} to secondary group {groupname}")


def delete_user(username):
    # Delete user and their home directory
    subprocess.run(['userdel', '-r', username])
    print(f"Deleted user {username}")


def delete_group(groupname):
    # Delete a group
    subprocess.run(['groupdel', groupname])
    print(f"Deleted group {groupname}")


def create_users_and_groups():
    # Iterate through users and set uid, shell, and username
    for i, user in enumerate(users):
        uid = uid_start + i
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
        else:
            # Special case where username cannot be constructed from full name from users list
            user_id = user
            user = "Varun Bhaskara"

        shell = '/bin/bash'
        home_dir = f'/home/{user_id}'
        create_user(user_id, user, uid, home_dir, shell)
        print(f"Created user {user_id} with UID: {uid}, GID: {uid}, home_dir: {home_dir}, shell: {shell}")

    for group, members in secondary_group.items():
        create_group(group, members)


def delete_users_and_groups():
    # Iterate through groups and delete them
    for group in secondary_group.keys():
        delete_group(group)

    # Iterate through users and delete them
    for user in users:
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
        else:
            # Special case where username cannot be constructed from full name from users list
            user_id = user
        delete_user(user_id)


# def set_umask(umask_value="0007"):
#     umask_line = f"umask {umask_value}"
#
#     with open("/etc/profile.d/umask.sh", 'r+') as file:
#         contents = file.readlines()
#
#         for i, line in enumerate(contents):
#             if line.strip().startswith("umask"):
#                 contents[i] = umask_line + "\n"
#                 break
#         else:
#             # Insert umask at the top of the /etc/profile file
#             contents.insert(0, umask_line + "\n")
#
#         file.seek(0)
#         file.writelines(contents)
#
#     subprocess.run(['bash', '-c', 'source /etc/profile'])
#     print(f"Updated umask value to {umask_value}")


def set_umask(umask_value="0007"):
    umask_line = f"umask {umask_value}"
    custom_script_path = "/etc/profile.d/umask.sh"

    with open(custom_script_path, 'w') as file:
        file.write(umask_line + "\n")

    print(f"Updated umask value to {umask_value} in {custom_script_path}")

def add_sys_admin(username='vabh4134'):
    if distro.name() == 'Rocky Linux':
        group = 'wheel'
    else:
        group = 'sudo'
    subprocess.run(['usermod', '-aG', group, username])
    print(f"Added Sys admin user to {group} group {username}")


def rename_files(dir_path="/home"):
    for i, user in enumerate(users):
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
            old_path = os.path.join(dir_path, user_id)
            new_path = os.path.join(dir_path, f"{user_id}_backup")

            try:
                os.rename(old_path, new_path)
                print(f'Renamed directory: {user_id} to {f"{user_id}_backup"}')
            except Exception as e:
                print(f'Failed to rename directory {old_path}: {str(e)}')


def copy_files(dir_path="/home"):
    for i, user in enumerate(users):
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
            old_path = os.path.join(dir_path, user_id)
            new_path = os.path.join(dir_path, f"{user_id}_backup")

            files_to_copy = glob.glob(os.path.join(new_path, '*'))

            if files_to_copy:
                cmd = ['install', '-m', '700', '-o', user_id, '-g', user_id] + files_to_copy + [old_path]
                subprocess.run(cmd)


def delete_backups(dir_path="/home"):
    for i, user in enumerate(users):
        names = user.split()
        if len(names) > 1:
            user_id = names[0][0].lower() + names[-1].lower()
            path = os.path.join(dir_path, f"{user_id}_backup")
            try:
                shutil.rmtree(path)
                print(f"Directory {dir_path} has been removed successfully.")
            except OSError as e:
                print(f"Error: {e}")


def create_shared_directories(dir_path="/home"):
    for group in secondary_group.keys():
        path = os.path.join(dir_path, group)
        os.makedirs(path, exist_ok=True)
        print(f"Created folder for secondary group {group} as {path}")
        subprocess.run(['chmod', '2770', path])
        subprocess.run(['chown', f":{group}", path])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true", help="Create users, home directories, and groups.")
    parser.add_argument("--delete", action="store_true", help="Delete users, home directories, and groups.")
    parser.add_argument("--umask", action="store_true", help="Set the umask value for new directories.")
    parser.add_argument("--rename", action="store_true", help="Rename files in Machine E")
    parser.add_argument("--copy", action="store_true", help="Copy files from backup to main on Machine E")
    parser.add_argument("--shared", action="store_true", help="Create shared directories on Machine E")
    args = parser.parse_args()

    if args.create:
        create_users_and_groups()
        add_sys_admin()
    elif args.delete:
        delete_users_and_groups()
    elif args.umask:
        set_umask()
    elif args.rename:
        if socket.gethostname().split(".")[0] == "machinee":
            rename_files()
        else:
            print("Unable to perform this action on this machine")
    elif args.copy:
        if socket.gethostname().split(".")[0] == "machinee":
            copy_files()
            delete_backups()
        else:
            print("Unable to perform this action on this machine")
    elif args.shared:
        if socket.gethostname().split(".")[0] == "machinee":
            create_shared_directories()
        else:
            print("Unable to perform this action on this machine")
    else:
        print("Please specify either --create or --delete.")
