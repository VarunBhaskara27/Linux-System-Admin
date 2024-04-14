import subprocess
import os
import shutil
import socket
import argparse
import distro

distro = distro.name().split(" ")[0]

if distro == "Debian":
    apache = 'apache2'
else:
    apache = 'httpd'

sites = {
    'dundermifflin': 'www.dundermifflin.com',
    'michaelscottpapercompany': 'www.michaelscottpapercompany.com',
    'schrutefarms': 'www.schrutefarms.com'
}


def install_web_server(machine):
    subprocess.run(['apt', 'update'], check=True)
    subprocess.run(['apt', 'install', 'apache2', '-y'], check=True)
    subprocess.run(['apt', 'install', 'rsync', '-y'], check=True)
    print(f"Installed Apache web server and Rsync on machine {machine}")


def create_cgi_script():
    if distro == "Debian":
        subprocess.run(['a2enmod', 'cgi'], check=True)
    else:
        httpd_conf = "/etc/httpd/conf/httpd.conf"
        new_cgi_path = "/usr/lib/cgi-bin"

        with open(httpd_conf, "r") as conf_file:
            httpd_conf_contents = conf_file.read()
            httpd_conf_contents = httpd_conf_contents.replace('<Directory "/var/www/cgi-bin">',
                                                              f'<Directory "{new_cgi_path}">')
        with open(httpd_conf, "w") as conf_file:
            conf_file.write(httpd_conf_contents)

    command = ["htpasswd", "-i", "-c", f"/etc/{apache}/.htpasswd", "webmaster"]
    execute = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    execute.communicate(input=b"dm23")
    print(f"Setup user webmaster")
    subprocess.run(['chmod', 'o+rx', f"/etc/{apache}/.htpasswd"])
    subprocess.run(['systemctl', 'restart', apache], check=True)
    print(f"Enabled CGI Scripts in the {apache} Configuration")


def create_custom_content():
    if distro == "Rocky":
        int = "#!/usr/bin/python"
        log_file = f"/var/log/httpd/dundermifflin"
    else:
        int = "#!/usr/bin/python3"
        log_file = "${{APACHE_LOG_DIR}}"

    script = f"{int}\n" + r"""
import os
import subprocess

def create_script_body(directory, path="/var/www/html"):
   files = [file for dir_path, dir_names, file_names in os.walk(os.path.join(path, directory)) for file in file_names]
   return f"<tr><td>{directory}.com</td><td>{len(files)}</td><td>{subprocess.check_output(['du', '-sh', os.path.join(path, directory)]).split()[0].decode('utf-8')}</td></tr>"

print("Content-type: text/html\r\n\r\n")
print("<h1>Disk Usage</h1>\r\n")

print("<table border='1'><tr><th>Site</th><th>Files</th><th>Size</th></tr>\n")
""" + """
print(f"{create_script_body('dundermifflin')}\\n")
print(f"{create_script_body('michaelscottpapercompany')}\\n")
print(f"{create_script_body('schrutefarms')}\\n")
print("</table>")
"""

    cgi_path = "/usr/lib/cgi-bin"
    if distro == "Debian":
        with open(os.path.join(cgi_path, 'diskusage'), "w") as cgi_script:
            cgi_script.write(script)

        subprocess.run(['chmod', 'o+rx', os.path.join(cgi_path, 'diskusage')])

    create_cgi_script()
    cgi_script_content = f"""
ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
<Directory {cgi_path}>
    Options +ExecCGI
    AddHandler cgi-script .py
    AuthType Basic
    AuthName "Restricted Area"
    AuthUserFile /etc/{apache}/.htpasswd
    require user webmaster
</Directory>"""

    virtual_host_config = f"""
<VirtualHost *:80>
    ServerName dundermifflin.com
    ServerAlias www.dundermifflin.com
    ServerAdmin vabh4134@colorado.edu
    DocumentRoot /var/www/html/dundermifflin/
    LogLevel debug
    ErrorLog {log_file}/error.log
    CustomLog  {log_file}/access.log combined
    {cgi_script_content}
</VirtualHost>"""

    if distro == "Debian":
        subprocess.run(['a2dissite', 'dundermifflin.com'], check=True)
        with open(os.path.join("/etc/apache2/sites-available", "dundermifflin.com.conf"), "w") as config_file:
            config_file.write(virtual_host_config)
        subprocess.run(['a2ensite', 'dundermifflin.com'], check=True)
    else:
        with open(os.path.join("/etc/httpd/conf.d", "dundermifflin.com.conf"), "w") as config_file:
            config_file.write(virtual_host_config)
        subprocess.run(['systemctl', 'enable', apache], check=True)

    subprocess.check_output(['apachectl', 'configtest'])
    subprocess.run(['systemctl', 'restart', apache], check=True)


def configure_web_server(path="/var/www/html"):
    ## TAKE CARE OF UMASK IN /ETC/PROFILE ##
    for directory, host in sites.items():
        if distro == "Debian":
            shutil.copytree(os.path.join("/root", directory), os.path.join(path, directory))
            apache_path = "/etc/apache2/sites-available"
            subprocess.run(['chown', '-R', 'www-data:', os.path.join(path, directory)])
            log_file = "${{APACHE_LOG_DIR}}"
        else:
            apache_path = "/etc/httpd/conf.d"
            subprocess.run(['chown', '-R', 'apache:', os.path.join(path, directory)])
            log_file = f"/var/log/httpd/{directory}"
            subprocess.run(['mkdir', '-p', log_file])
        # subprocess.run(['chmod', '-R', 'o+rx', os.path.join(path, directory)])
        print(f"Created directory in ${path} for ${directory} and moved contents")

        virtual_host_config = f"""
<VirtualHost *:80>
    ServerName {'.'.join(host.split('.')[1:])}
    ServerAlias {host}
    ServerAdmin vabh4134@colorado.edu
    DocumentRoot {os.path.join(path, directory)}
    LogLevel warn
    ErrorLog {log_file}/error.log
    CustomLog  {log_file}/access.log combined
 </VirtualHost>"""

        with open(os.path.join(apache_path, f"{'.'.join(host.split('.')[1:])}.conf"), "w") as config_file:
            config_file.write(virtual_host_config)

        if distro == "Debian":
            subprocess.run(['a2ensite', '.'.join(host.split('.')[1:])], check=True)
        else:
            subprocess.run(['systemctl', 'enable', apache], check=True)
        print(f"Created Virtual Host file for ${directory}")

    try:
        subprocess.run(['apachectl', 'configtest'], check=True)
        print("Config looks good!")
    except subprocess.CalledProcessError:
        print("Please check config as there is an error")

    subprocess.run(['systemctl', 'restart', apache], check=True)
    print(f"Restarted {apache} to apply changes")


def destroy_web_server(path="/var/www/html", apache_path="/etc/apache2/sites-available"):
    for directory in sites.keys():
        dir_path = os.path.join(path, directory)

        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Removed {directory} from {path}")

    for directory, host in sites.items():
        virtual_host_config_file = os.path.join(apache_path, f"{'.'.join(host.split('.')[1:])}.conf")

        if os.path.exists(virtual_host_config_file):
            os.remove(virtual_host_config_file)
            print(f"Removed virtual host config file {virtual_host_config_file}")

        subprocess.run(['a2dissite', '.'.join(host.split('.')[1:])], check=True)
        print(f"Disabled Virtual Host file for {directory}")

    subprocess.run(['systemctl', 'restart', 'apache2'], check=True)
    print(f"Restarted apache2 to apply changes")

    subprocess.run(['rm', '/etc/apache2/.htpasswd'])
    print(f"Removed password files")

    subprocess.run(['rm', '/usr/lib/cgi-bin/diskusage'])
    print(f"Removed diskusage file")


# def update_hosts_file(ip_addr="100.64.9.3"):
#     dns_entries = f"""
# {ip_addr}  www.dundermifflin.com dundermifflin.com
# {ip_addr}  www.michaelscottpapercompany.com michaelscottpapercompany.com
# {ip_addr}  www.schrutefarms.com schrutefarms.com"""
#
#     with open('/etc/hosts', 'a') as hosts_file:
#         hosts_file.write(dns_entries)
#     print("Updated /etc/hosts file with DNS entries.")


def provide_access(site, users, group, path="/var/www/html"):
    subprocess.run(['groupadd', group])
    print(f"Created group {group} for {site}")
    for user in users:
        subprocess.run(['usermod', '-aG', group, user])
        print(f"Added member {user} to site group {group}")
    subprocess.run(["chmod", "-R", "2770", os.path.join(path, site)], check=True)
    subprocess.run(["chown", "-R", f":{group}", os.path.join(path, site)], check=True)
    for user in users:
        print(f"{user} can now modify {site}")


def do_mirroring(user, ip_addr, sources):
    ## SETUP PASSWORDLESS LOGIN FROM MACHINE D TO C LIKE IN LAB 3 ##
    destinations = [x.rstrip('/') for x in sources]
    subprocess.run(['dnf', 'update', '-y'], check=True)

    subprocess.run(['dnf', 'install', '-y', 'httpd'], check=True)
    subprocess.run(['systemctl', 'unmask', 'httpd'], check=True)
    subprocess.run(['systemctl', 'enable', 'httpd'], check=True)
    subprocess.run(['systemctl', 'start', 'httpd'], check=True)

    subprocess.run(['systemctl', 'disable', 'firewalld'], check=True)
    subprocess.run(['systemctl', 'stop', 'firewalld'], check=True)

    subprocess.run(['dnf', 'install', '-y', 'rsync'], check=True)
    print("Installed Rsync on Machine")

    for d in destinations:
        subprocess.run(['mkdir', '-p', d + "/"], check=True)
        print(f"Created directory {d}")

    with open('mirror_cron', 'w') as file:
        for s, d in zip(sources, destinations):
            entry = f"*/5 * * * * rsync -r -avz --perms --no-owner --no-group -e ssh {user}@{ip_addr}:{s} {d}\n"
            # entry = f"*/5 * * * * rsync -r -avz --perms --no-owner --no-group --exclude 'dundermifflin/accounting/' -e ssh {user}@{ip_addr}:{s} {d}\n"
            file.write(entry)

    subprocess.run('crontab mirror_cron', shell=True)
    subprocess.run('rm mirror_cron', shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install Apache Web Server on machine")
    parser.add_argument("--configure", action="store_true", help="Configure Web server")
    parser.add_argument("--destroy", action="store_true", help="Destroy Config for Web server")
    parser.add_argument("--hosts", action="store_true", help="Update hosts file")
    parser.add_argument("--access", action="store_true", help="Provide access to users to web server files")
    parser.add_argument("--addcgi", action="store_true", help="Provide access to users to web server files")
    parser.add_argument("--mirror", action="store_true", help="Mirror files to Machine D")
    args = parser.parse_args()

    allowed_hosts = ["machinec", "machined"]

    if socket.gethostname().split(".")[0] in allowed_hosts:
        if args.install:
            install_web_server(socket.gethostname().split(".")[0])
        elif args.configure:
            configure_web_server()
        elif args.destroy:
            destroy_web_server()
        elif args.hosts:
            # update_hosts_file()
            pass
        elif args.access:
            provide_access("dundermifflin", ["pbeesly", "abernard", "kkapoor"], "dundermifflinusers")
            provide_access("schrutefarms", ["dschrute"], "schrutefarmsusers")
        elif args.addcgi:
            create_custom_content()
        elif args.mirror:
            do_mirroring("root", "100.64.9.3", ["/var/www/html/", "/usr/lib/cgi-bin/"])
    else:
        print("This action is not supported on this machine")
