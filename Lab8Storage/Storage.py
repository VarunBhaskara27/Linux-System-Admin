import argparse
import subprocess
import shutil
import os

drives = ['/dev/sdb', '/dev/sdc', '/dev/sdd', '/dev/sde']

cur_users = ["vabh4134", "mscott", "dschrute", "kkapoor", "pbeesly", "abernard", "amartin",
             "kmalone", "omartinez", "jhalpert", "tflenderson", "cbratton", "dphilbin", "mpalmer", "plapin", "shudson"]

cur_groups = ['managers', 'sales', 'accounting']


def run_command(command):
    try:
        out = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        print(f"Output: {out.decode()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output.decode()}")
        return False


def create_partition():
    for d in drives:
        command = f"echo -e 'n\np\n1\n\n\nt\n8e\nw' | fdisk {d}"
        if run_command(command):
            print(f"Created a single partition for disk {d}")


def create_raid_array():
    raid_array = ' '.join([x + '1' for x in drives])
    command = f"mdadm --create --verbose /dev/md0 --raid-devices=4 --level=5 {raid_array}"
    if run_command(command):
        print(f"Created a raid array using partitions{raid_array}")
        with open("/etc/mdadm.conf", "a") as f:
            subprocess.run(['mdadm', '--verbose', '--detail', '--scan'], stdout=f, check=True)
        print("Saved RAID config at /etc/mdadm.conf")


def create_volume_group():
    command = "pvcreate /dev/md0"
    if run_command(command):
        print("Physical volume created")
        command = "vgcreate savg /dev/md0"
        if run_command(command):
            print("Volume group savg created")


def create_logical_volume(name, space, filesystem):
    if '%' in space:
        size_ind = 'l'
    else:
        size_ind = 'L'
    command = f"lvcreate -n {name} -{size_ind} {space} savg"
    if run_command(command):
        print(f"Created logical volume {name} with space {space}")
        command = f"mkfs -t {filesystem} /dev/mapper/savg-{name}"
        if run_command(command):
            print(f"Created {filesystem} on logical volume {name}")


def do_mount():
    subprocess.run(['sudo', 'yum', '-y', 'install', 'quota'], check=True)
    print("Installed quota")

    shutil.move('/tmp', '/tmp_backup')
    print("Moved files from /tmp to /tmp_backup")
    shutil.move('/home', '/home_backup')
    print("Moved files from /home to /home_backup")

    fstab_entries = [
        "/dev/savg/tmp /tmp ext4 defaults,nodev,nosuid,noexec 0 0\n",
        "/dev/savg/home /home xfs defaults,nodev,uquota,gquota 0 0\n",
    ]

    with open('/etc/fstab', 'a') as fstab_file:
        for line in fstab_entries:
            fstab_file.write(line)
            print(f"Added entry {line} to /etc/fstab")

    os.makedirs("/home")
    os.makedirs("/tmp")

    subprocess.run(['mount', '-a'])
    print("Mounted new file systems")

    shutil.copytree('/tmp_backup', '/tmp', dirs_exist_ok=True)
    shutil.copytree('/home_backup', '/home', dirs_exist_ok=True)
    print("Copied over content from old disk to new ones")

    shutil.rmtree('/tmp_backup')
    shutil.rmtree('/home_backup')
    print("Removed old backups")


def add_quota():
    for user in cur_users:
        subprocess.run(["xfs_quota", "-x", "-c", f"limit -u bsoft=1000m bhard=1200m {user}", "/home"], check=True)
        print(f"Added soft and hard limit for user {user}")
    for group in cur_groups:
        subprocess.run(["xfs_quota", "-x", "-c", f"limit -g bsoft=1000m bhard=1200m {group}", "/home"], check=True)
        print(f"Added soft and hard limit for group {group}")
    subprocess.run(["xfs_quota", "-x", "-c", f"timer -u -bir 1day", "/home"], check=True)
    print(f"Added grace period of 1 day for blocks, inodes and realtime blocks for users")
    subprocess.run(["xfs_quota", "-x", "-c", f"timer -g -bir 1day", "/home"], check=True)
    print(f"Added grace period of 1 day for blocks, inodes and realtime blocks for groups")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", action="store_true", help="Create Partitions on each drive")
    parser.add_argument("--raid", action="store_true", help="Create RAID array using the partitions")
    parser.add_argument("--vg", action="store_true", help="Create a volume group using the Physical Volume")
    parser.add_argument("--lv", action="store_true", help="Create a logical volume using the volume group")
    parser.add_argument("--mount", action="store_true", help="Mount volumes and free up space")
    parser.add_argument("--quota", action="store_true", help="Add user and group quotas")
    args = parser.parse_args()

    if args.partition:
        create_partition()
    elif args.raid:
        create_raid_array()
    elif args.vg:
        create_volume_group()
    elif args.lv:
        create_logical_volume("tmp", "1G", "ext4")
        create_logical_volume("home", "80%FREE", "xfs")
    elif args.mount:
        do_mount()
    elif args.quota:
        add_quota()
