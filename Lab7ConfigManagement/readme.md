**Background**

Maintaining individual machines is becoming a major headache. For example, users change passwords on one machine and then pester you with password resets. You decide to do Configuration Management with Ansible to help streamline the process.

Machine E will be your control node. To keep things simple, you decide to set up ansible to use the personal login of the sysadmin to access managed machines (rather than set up an ansible user) and then elevate permissions using sudo. However, you should write the playbooks such that if a second administrator is hired, he or she could use the same playbooks without modification.

**Assignment**

1.  Set up password-less login for yourself (the sysadmin with user name
    the same as your identikey) from Machine E to all other machines.
    You should already have sudo access on all machines from this login.
2.  Install ansible on Machine E from the Rocky Linux repository using
    dnf.
3.  On Machine E, set up an ansible host group named saclass which
    contains the IP address of Machines A, B, C, D and F.
4.  On Machine E, create a script named mkdmuserplay that reads
    /etc/passwd, /etc/shadow and /etc/group and creates an ansible
    playbook called dmusers.yaml to set all the parameters (login, UID
    and GID, gecos, shell, groups, password hash, etc) for all
    Dunder-Mifflin users and groups. The script must be stored in the
    sysadmin home directory and create the YAML file in the current
    working directory. The script must ensure that I can run the
    playbook as you.
5.  Apply the dmusers playbook to machines A, B, C, D and F to ensure
    that the user information is the same on all machines.
6.  Rename the file you used to set the umask in Lab 3 to
    /etc/profile.d/umask.sh on all machines. Create a playbook named
    umask.yaml in your home directory to copy this file from Machine E
    to machines A, B, C, D and F. The file must have root as the owner
    and group root and permissions rw for the owner and r for the group
    and other.
7.  Correct any issues from Lab 3 and then use the playbook to make sure
    that the file on machines A, B, C, D and F is the same as on Machine
    E.
8.  Students in 5113: Create a single playbook on Machine E named
    webcheck.yaml that will make sure that the web servers on Machined C
    and D are at their latest version and that the web server is running
    and will start on boot.

**Hints:**

1.  Case matters in Linux/Unix. Do not introduce arbitrary upper case
    letters in file names, user or group names. This will cause the
    grading script to mark various tasks as failed.
2.  Be very careful about groups. You may have groups that exist on
    machines in the DMZ that does not exist on Machine E. The dmusers
    playbook MUST ensure that the managers, accounting and sales groups
    are present on all machines and contain the right users without
    messing up special groups on the DMZ machines. Also watch out for
    wheel or sudo groups.
3.  I should only need to provide ONE password to run the playbook. The
    remote user for the playbooks should be the user running it, and
    then rely on sudo to execute commands that are privileged.
4.  Ansible allows you to do all kinds of clever things in playbooks.
    If this is your first time to use ansible, apply the KISS principle.
    There are builtin Ansible modules to perform the tasks needed here,
    you don't need to create new modules.
5.  The location and name of the mkdmuserplay is critical. Do not add
    an extension such as .py or .sh to it. On Unix/Linux the #! line
    serves that function.
6.  Make sure the YAML files are in your home directory. That is where
    the grading script expects to find it.
