import os
import socket
import argparse
import distro
import subprocess

distro = distro.name().split(" ")[0]


def install_web_server(machine):
    subprocess.run(['apt', 'update'], check=True)
    subprocess.run(['apt', 'install', 'libpam-pwquality', '-y'], check=True)
    print(f"Installed Apache libpam-pwquality on machine {machine}")


def allow_logins(machine):
    file_path = "/etc/pam.d"
    enable_line = "account required pam_access.so\n"

    if distro == "Rocky":
        files = ["system-auth", "password-auth"]
        for file in files:
            pam_file = os.path.join(file_path, file)
            with open(pam_file, "r") as f:
                lines = f.readlines()

            if enable_line not in lines:
                for i in range(len(lines)):
                    if lines[i].strip().startswith("account") and not lines[i + 1].strip().startswith("account"):
                        lines.insert(i + 1, enable_line)
                        with open(pam_file, "w") as f2:
                            f2.writelines(lines)
                        print(f"Added line {enable_line} in file ${pam_file} in distro ${distro}")
                        break
            else:
                print(f"Config {enable_line} already exists in file ${pam_file} in distro ${distro}")
    else:
        files = ["login", "sshd"]
        install_web_server(machine)
        for file in files:
            pam_file = os.path.join(file_path, file)
            with open(pam_file, "r") as f:
                lines = f.readlines()
            for i in range(len(lines)):
                if " ".join(lines[i].split()) == f"# account required pam_access.so":
                    lines[i] = " ".join(lines[i].split()).replace("# ", "")
                    with open(pam_file, "w") as f2:
                        f2.writelines(lines)
                    print(f"Uncommented line {enable_line} in file ${file} in distro ${distro}")
                    break
            else:
                print(f"Config {enable_line} already exists in file ${file} in distro ${distro}")

    access_rules = [
        f"+:root vabh4134 mscott dschrute:ALL",
        f"+:pbeesly abernard kkapoor:ALL" if machine in ("machinec", "machined") else "",
        f"+:(accounting):ALL" if machine == "machinef" else "",
        f"+:jhalpert tflenderson cbratton dphilbin amartin kmalone omartinez mpalmer kkapoor pbeesly abernard plapin shudson:ALL" if machine == "machinee" else "",
        "-:ALL:ALL"
    ]

    with open("/etc/security/access.conf", "a") as access:
        for rule in access_rules:
            if rule:
                access.write(rule + "\n")


def destroy_config():
    with open("/etc/security/access.conf", "r") as access:
        lines = access.readlines()
    new_lines = [line for line in lines if line.startswith("#")]
    with open("/etc/security/access.conf", "w") as access1:
        access1.writelines(new_lines)
    with open("/etc/security/pwquality.conf", "r") as pw:
        pw_lines = pw.readlines()
    new_pw_lines = [line for line in pw_lines if line.startswith("#")]
    with open("/etc/security/pwquality.conf", "w") as pw1:
        pw1.writelines(new_pw_lines)
    print(f"Cleaned access config file removed lines {[line for line in lines if not line.startswith('#')]}")
    print(f"Cleaned pwquality config file removed lines {[line for line in pw_lines if not line.startswith('#')]}")


def password_policy():
    policy = {"minlen": 10, "minclass": 3, "dcredit": -2, "ucredit": -2, "ocredit": -1, "lcredit": 0}
    other_measures = ["local_users_only", "enforce_for_root"]
    with open("/etc/security/pwquality.conf", "a") as pw:
        for key, value in policy.items():
            pw.write(f"{key} = {value}\n")
        for val in other_measures:
            pw.write(val + "\n")
    print("Created password policy!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--configure", action="store_true", help="Configure access rules")
    parser.add_argument("--policy", action="store_true", help="Configure password policy")
    parser.add_argument("--destroy", action="store_true", help="Destroy access rules and policy")
    args = parser.parse_args()

    if args.configure:
        devices = ["machinea", "machineb", "machinec", "machined", "machinee", "machinef"]
        # devices = ["debian", "localhost"]
        for device in devices:
            if socket.gethostname().split(".")[0] == device:
                allow_logins(device)
    elif args.destroy:
        destroy_config()
    elif args.policy:
        password_policy()
