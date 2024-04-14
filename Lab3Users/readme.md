**Prerequisites**

Review the Dunder Mifflin Scenario and familiarize yourself with the network and employees.

Make sure you can access the machines via ssh so that you can scp scripts to and from your machines. Doing this assignment from the console will be very difficult. To access Machine E via ssh, you first need to ssh to Machine A and from there ssh to Machine E.

**Assignment**

Write a script to create logins for all Dunder Mifflin employees on all machines. Students in 4113 and 5030 only need to apply this script on the Linux Machines A-F. Students in 5113 must also use it on the FreeBSD Machine X.

I will use an automated grading script to evaluate your work so make sure that for all employees you use the exact username shown in the scenario. For your own username, use your identikey login.

**Requirements:**

1.  Each user should have a username and user private group of the form first-initial last-name, password, unique uid, unique gid, /path/to/login/shell, and /path/to/home/directory/. The grading script is very strict about user names and groups, so use exactly the names shown in the table at the bottom of the scenario. The Gecos field should have their name.
2.  User information and passwords must be the same on all machines.
3.  Home directories must exist for all users. Home directory names must match the user name. All home directories on all machines must be initialized with the contents of /etc/skel/ and owned by the appropriate user and user-private-group.
4.  Permissions for home directories must be read, write and execute for the owner and no access for the group or others.
5.  Create secondary groups named managers, sales, and accounting. Add the appropriate users to these groups based on the org chart. Managers are those persons with manager in their title, not others that may have supervisory duties.
6.  Create a shared directory under /home/ on the file server (Machine E) for each secondary group you created, with permissions such that only the owner and members of the group can read, write, and execute files. New files and folders created under these shared directories must inherit the group id of the parent directory, not that of the process that creates them.
7.  Machine E has some existing user directories and files that should be integrated into this assignment with appropriate ownership and permissions. Do not copy these files to other machines.
8.  Add the system administrator (you) to the wheel or sudo groups so that you can run commands using sudo.
9.  Adjust the umask on all machines so that, when new directories are created, the owner can read, write, and execute, the group can read, write and execute, and others have no access.

**Hints:**

1.  It would be expedient to have the Dunder-Mifflin employees have a unique range of UIDs, say 3000-3999.
2.  The script should not simply be a long sequence of commands. Use functions and loops to perform repetitive tasks.
3.  You may want to create scripts to add all the users to a machine and another to remove these users so that you can experiment, but be careful about existing files on Machine E.
4.  You may want to use you Virtualbox machines to try things out first.
5.  Use scp to move your scripts around - things can go awry with cut and paste.
6.  You can set the default umask by adding one file, instead of modifying existing files. Read the header of the /etc/bashrc file
    on Rocky 9 machines.
7.  If you resort to ACLs to accomplish any of these tasks, you are totally missing the point.
