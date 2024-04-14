#!/usr/bin/python3
import os

etc_dir = "/etc"
users = os.path.join(etc_dir, "passwd")
groups = os.path.join(etc_dir, "group")
password = os.path.join(etc_dir, "shadow")

cur_users = ["vabh4134", "mscott", "dschrute", "kkapoor", "pbeesly", "abernard", "amartin",
             "kmalone", "omartinez", "jhalpert", "tflenderson", "cbratton", "dphilbin", "mpalmer", "plapin", "shudson"]

cur_groups = ['managers', 'sales', 'accounting']
dmzgroups = ['dundermifflinusers', 'schrutefarmsusers', 'wheel', 'sudo']


def read_lines_func(file):
    with open(file, "r") as opened_file:
        lines = opened_file.readlines()
    return lines


def make_group_var():
    dm_group_var = "    dmgroups:\n"
    lines = read_lines_func(groups)
    for line in lines:
        if line.split(":")[0] in cur_groups+cur_users:
            dm_group_var += f"     - name: {line.split(':')[0]}\n"
            dm_group_var += f"       gid: {line.split(':')[2]}\n"
            dm_group_var += "\n"
    return dm_group_var


def get_user_groups():
    dict = {}
    lines = read_lines_func(groups)
    for l in lines:
        if l.split(':')[3].strip() != '':
            for i in l.split(':')[3].split(","):
                if l.split(':')[0] not in dmzgroups:
                    dict[i.strip()] = dict.get(i.strip(), []) + [l.split(':')[0]]
    return dict


def make_user_var():
    dm_user_var = "    dmusers:\n"
    lines = read_lines_func(users)
    pwdlines = {i.split(':')[0]: i.split(':')[1] for i in read_lines_func(password) if
                i.split(':')[0] in (i.split(":")[0] for i in lines)}
    res = get_user_groups()
    for line in lines:
        if line.split(":")[0] in cur_users:
            dm_user_var += f"     - name: {line.split(':')[0]}\n"
            dm_user_var += f"       uid: {line.split(':')[2]}\n"
            dm_user_var += f"       group: {line.split(':')[0]}\n"
            dm_user_var += f"       home: {line.split(':')[5]}\n"
            dm_user_var += f"       shell: {line.split(':')[6].strip()}\n"
            dm_user_var += f"       comment: {line.split(':')[4]}\n"
            dm_user_var += f"       password: {pwdlines[line.split(':')[0]]}\n"
            try:
                val = ','.join(res[line.split(':')[0]])
                dm_user_var += f"       groups: {val}\n"
            except KeyError:
                dm_user_var += "\n"
            dm_user_var += "\n"
    return dm_user_var

def create_ansible_user_tasks():
    create_user_task = "   - name: Create Dunder Mifflin Users\n"
    create_user_task += "      user:\n"
    create_user_task += "       name: \"{{ item.name }}\"\n"
    create_user_task += "       uid: \"{{ item.uid }}\"\n"
    create_user_task += "       group: \"{{ item.group }}\"\n"
    create_user_task += "       home: \"{{ item.home }}\"\n"
    create_user_task += "       shell: \"{{ item.shell }}\"\n"
    create_user_task += "       comment: \"{{ item.comment }}\"\n"
    create_user_task += "       password: \"{{ item.password }}\"\n"
    create_user_task += "       groups: \"{{ item.groups | default([]) }}\"\n"
    create_user_task += "       append: true\n"
    create_user_task += "      loop: \"{{ dmusers }}\"\n"
    return create_user_task

def create_ansible_group_tasks():
    create_group_task = "   - name: Create Dunder Mifflin Groups\n"
    create_group_task += "      group:\n"
    create_group_task += "        name: \"{{ item.name }}\"\n"
    create_group_task += "        gid: \"{{ item.gid }}\"\n"
    create_group_task += "      loop: \"{{ dmgroups }}\"\n"
    return create_group_task


def create_sysadmin_user_task():
    create_sys_user_task = "   - name: Create Dunder SysAdmin Users\n"
    create_sys_user_task += "      user:\n"
    create_sys_user_task += "       name: vabh4134\n"
    create_sys_user_task += "       groups: \"{{ 'sudo' if ansible_distribution == 'Debian' else 'wheel' }}\"\n"
    create_sys_user_task += "       append: yes"
    return create_sys_user_task

def print_config():
    ansible_lines = "---\n"
    ansible_lines += "- name: 'Create Dunder Mifflin users and groups'\n"
    ansible_lines += "  hosts: saclass\n"
    ansible_lines += "  become: yes\n"
    ansible_lines += f"  vars:\n"
    ansible_lines += f"{make_group_var()}"
    ansible_lines += f"{make_user_var()}"
    ansible_lines += f"  tasks:\n"
    ansible_lines += f" {create_ansible_group_tasks()}\n"
    ansible_lines += f" {create_ansible_user_tasks()}\n"
    ansible_lines += f" {create_sysadmin_user_task()}\n"
    return ansible_lines


with open("dmusers.yaml", "w") as ans:
    ans.writelines(print_config())

