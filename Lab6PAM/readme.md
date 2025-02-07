**Background**

Users have ignored your new password policy and it has come to your attention that some users are logging into machines in the DMZ to avoid email filters on Machine E that block email with questionable content.

Michael Scott has agreed to let you limit who can log into each of the DMZ machines and to enforce a new password policy when users change their passwords.

**Assignment**

1.  Update all machines to limit who may login using the pam_access
    module. The entries for Dunder-Mifflin users in /etc/password and
    /etc/shadow must be the same across all machines. Who may log in
    must be limited by PAM.
2.  Users root, the system administrator (you), Michael Scott and Dwight
    Schrute must be able to log into all machines.
3.  All users must be able to log in to Machine E.
4.  In addition to (2), only Pam Beesly, Andy Bernard and Kelly Kapoor
    must be able to log in to Machine C and Machine D.
5.  In addition to (2), only members of the accounting group must be
    able to log into Machine F. The password policy must be enforced on
    all machines using PAM. Passwords must be at least 10 characters
    long, and contain at least 2 digits, 2 uppercase, and 1 non
    alphanumeric character. Length credit must not be given for lower
    case characters. You must explicitly specify all the parameters
    involved because defaults are inconsistently implemented. Do not
    expire passwords. The policy only applies to password changes.
6.  Students in 5113: Provide a description of how you would limit DM
    employees other than root, yourself and Dwight Schrute to only be
    able to log in to a system between 7am and 6pm on weekdays. Do not
    apply apply this limitation. Simply describe the specific method
    you would use to implement this restriction.
7.  Extra credit (25%): Provide a script that will test whether you
    completed parts 1, 2, 4 and 5 of the assignment correctly on
    machines A,B, C, D and F for all Dunder-Mifflin users but not root.
    The script must be called lab6-check, use the #! header to set the
    appropriate interpreter and require no command line parameters to
    run. That does mean you will need to include passwords in the
    script which is a huge security risk, so set a throw away password
    for these users. We will fix this in Lab 7. The script must verify
    that the designated users can log into the various machines, and
    that other users can not log in. The output from the script should
    be something like this

    Machine A
    1 mscott can log in
    0 dschrute should be able to log in
    0 pbeesly should not be able to log in
    1 abernard cannot log in
    ...
    Machine B
    ...

The leading 1 indicates that this is correct, a 0 indicates that this is not correct. If you did he assignment correctly, there should be no leading 0s. I will run your script on an Ubuntu machine connected to the VPN.

1.  Extra extra credit: You can earn an additional 5 extra credit
    points if your script uses data structures and loops to perform the
    test in a compact and elegant way.

**Hints.**

1.  These requirements are additive to previous labs. Make sure that
    you implement corrections pointed out by previous labs.
2.  On debian machines, you need to install the libpam-pwquality
    package.
