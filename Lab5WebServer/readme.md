**Background**

Instead of using the ISP to host the Dunder-Mifflin web site, Michael Scott has directed you to host the Dunder-Mifflin web site on Machine C in the DMZ.

As part of the agreement for Dunder-Mifflin to acquire the Michael Scott Paper Company, Dunder-Mifflin also hosted the web site of the now defunct Michael Scott Paper Company.

Dwight Schrute has convinced Michael that all the websites at the ISP must be moved together, so the server should also host the Schrute Farms web site because that is how web sites work.

The ISP has emailed you the files for the Dunder Mifflin, Michael Scott Paper Company and Schrute Farms web sites.

**Assignment**

1.  Install an Apache server on Machine C.
2.  Configure Apache to have virtual hosts for Dunder-Mifflin
    (www.dundermifflin.com), the Michael Scott Paper Company
    (www.michaelscottpapercompany.com) and Schrute Farms
    (www.schrutefarms.com).
3.  Configure Apache to accept both the full hostname and omitting the
    leading www. So, for example both www.dundermifflin.com and
    dundermifflin.com should work.
4.  Pam Beesly, Kelly Kapoor and Andy Bernard must be able to add and
    edit files served by the web server but only on the Dunder Mifflin
    web server. Dwight Schrute should have similar privileges on the
    Schrute Farms web server. (Dwight has sudo access, but should not
    need to use it.)
5.  The DocumentRoot for each of the sites must be /var/www/html/site
    were the site must match the name as received from the ISP. For
    example, the Dunder Mifflin site should have a DocumentRoot of
    /var/www/html/dundermifflin.
6.  Students in 5030 & 5113: Configure Machine D as a backup web
    server. Use cron and rsync on Machine D to update the html files
    from Machine C every 5 minutes.

**Extra credit:**

1.  Create a CGI script that will report the number of files and disk
    space used by each of the three web sites. Configure it so that I
    can access it as http://www.dundermifflin.com/cgi-bin/diskusage (no
    extension). The output should look like this

    Disk Usage
    Site Files Size
    dundermifflin.com 294 4.3M
    michaelscottpapercompany.com 287 4.3M
    schrutefarms.com 6 84K

2.  Restrict access to this CGI script so that it requires a user name
    and password by using the Apache Authorization module. Set the user
    name to webmaster and the password to dm23 (both user name and
    password all lower case). Restrict access to this CGI script to
    only the dundermifflin.com domain.
3.  Graduate students: Add mirroring of the CGI script to machine D.

**Bonus Extra Credit**

1. Create a script named webcheck (no extensions, select the interpreter using the #! line) to check that you satisfy all the requirements of the assignment. The output from the script should be verbose and indicate what it checked and whether the test passed or failed. Include both the script and the output from the script in your writeup.
2. Graduate students must also check the backup web server.

**Hints:**

1.  Test that your system behaves as required by checking that you can
    retrieve the pages using Apache, including those created by Pam,
    Andy and Kelly. Make sure they can read and modify existing files
    and files created by others in this group without having to run
    chmod. This is exactly what the grading script will do.
2.  Since these are virtual web servers, Apache relies on the hostname
    to decide what site to serve. Therefore you must make up an
    artificial DNS entry to point at your web servers. On
    Linux/Unix/OSX you can do this by adding an temporary entries in
    your /etc/hosts file or simply use curl as shown in Hint 3.

    100.64.N.3 www.dundermifflin.com dundermifflin.com
    100.64.N.3 www.michaelscottpapercompany.com michaelscottpapercompany.com
    100.64.N.3 www.schrutefarms.com schrutefarms.com

3.  Caching by a web browser can complicate testing. You can avoid it
    by using a program like curl. You can also readily test virtual
    servers by adding the resolv flag

    curl --resolv www.schrutefarms.com:80:100.64.N.3 http://www.schrutefarms.com/index.html
    curl --resolv www.dundermifflin.com:80:100.64.N.3 http://webmaster:dm22@www.dundermifflin.com/cgi-bin/diskusage

4.  Students in 5030 and 5113: Think carefully about the interaction of
    previous requirements with this assignment. For example, how does
    umask and rsync interact? Use only rsync, not a script to mess with
    permissions.

5.  Do not attempt to mirror the configuration files, only the content
    of the web sites.

6.  Pam, Andy and Kelley will only modify files on Machine C.

7.  Reboot machines C and D to make sure that your changes are
    permament.

8.  When you hear hooves, think horses not zebras. File access can be
    readily addressed using the Unix permissions. Don't immediately
    jump to more exotic approaches such as Access Control Lists. What to
    Submit:
