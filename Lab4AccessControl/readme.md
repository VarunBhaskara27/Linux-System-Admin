You have created accounts and removed root access for all Dunder-Mifflin employees. Now they have started complaining to you and Michael Scott that they can no longer do things that they once could. Michael Scott wants you to address these issues as soon as possible so that everyone calms down. You’ve received these emails so far:

You have received the following emails that you should respond to:

From: Pam Beesly
_I just wanted to let you know that Kelly Kapoor, Andy Bernard, and I now need need to type in our passwords every time we need to log into Machine C. It would be wonderful if you can set it up so that we can log in without a password like we used to! Thank you very much for your help!_

From: Dwight Schrute
_Your clever attempt to gain control of our Linux systems has worked, but only temporarily. Michael Scott will confirm that I must be granted administrative access on all servers. Please grant me access today, or else._

From: Jim Halpert
_Hey, quick question… can you grant me full administrative access on all of the servers? In the event that you are out of town I might need to access employee files or help them out with other things. My password is Dund3rMifflin if that makes it easier for you._

After checking with Michael Scott you are instructed to grant the requests from Pam and Dwight but not Jim.

Michael has agreed to let you create a password policy. He wants you to write a document defining the password requirements. Michael has also agreed that you may limit sudo access to only those who need it, as long as he retains the ability to shut down the servers in the DMZ.

**Assignment**

1.  Create a password policy in PDF format.
2.  Write an email to Jim responding to his request and point out the risk of including passwords in an email.
3.  Set up password-less logins for Pam Beesly, Kelly Kapoor and Andy Bernard from Machine E to Machine C.
4.  Allow Dwight Schrute to run any command via sudo on any machine using a method other than adding him to the sudo or wheel group.
5.  Allow Michael Scott to shut down any of the DMZ machines (B,C,D,F) with no less that two hours notice to other users. The shutdown command he will use is sudo shutdown -h followed by the number of minutes (an integer). As an upper limit you can assume that the shut down delay will be no more than 999 minutes. Michael should also be able to cancel the pending shutdown.
6.  Students in 5113: Allow Jim Halpert to change the ownership of files on Machine E to another user, but not the user root. So he should, for example, be able to make pbeesly the owner of a file, but not root.

**Hints:**

1.  You can do the entire sudo part of the assignment by modifying the /etc/sudoers. However, it would be expedient for future assignments if you do per machine customization by adding files to the /etc/sudoers.d.
2.  Make sure you fix problems from Lab 3. If the home directories for Pam, Kelly and Andy on Machine E are borked, password-less ssh is not going to work.
3.  Figure out how the Van Halen Brown M&M Clause applies to this assignment.
