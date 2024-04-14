**Background**

You have received a few ‘friendly’ e-mails from ‘management’ complaining that the they are unable to save the hillarious videos they downloaded from the internet on Machined E because the disk is full.

You have obtained some SATA drives and attached them to Machine E. (Students in 4113 and 5030 will find one unused drive /dev/sdb attached to Machine E. Students in 5113 will see four unused drives /dev/sdb, /dev/sdc, /dev/sdd and /dev/sde.) You decide to use the LVM to add more flexibility to your configuration of the machine and use the new drive to expand /tmp and /home on Machine E.

**Assignment**

1.  On Machined E, create a single Linux LVM partition on each of the
    new drives. The partition should use all of the recommended space
    available.
2.  Graduate students: Create a Linux software RAID array using the the
    four disks.
3.  Create a volume group named savg that uses all the newly added
    storage.
4.  Create a logical volume **tmp** that is 1GB in size and create an ext4
    file system on it.
5.  Create a logical volume home that fills 80% of the remainder of the
    newly added storage and create an xfs file system on it.
6.  Permanently add the new /tmp and /home filesystems to the root file
    system. Use the nodev, nosuid and noexec mount options for /tmp and
    the nodev mount option for /home.
7.  Extra credit (20%): Implement quotas on /home to limit the amount
    of storage that any Dunder-Mifflin employee may use to a soft limit
    of 1000MB, a hard limit of 1200MB and a grace period of 1 day.
    Apply the same limits to the managers, accounting and sales groups.

**Hints**

1.  You could use the entire disk for your physical volume or RAID array, but if you partition each disk and label it as a Linux LVM, the probability that you will accidentally trash the system is reduced. You do give up a small percentage of the available disk storage in the process. In this assignment, it is therefore required that you create the physical volume or RAID array in a partition instead of simply using the raw disk.
2.  Double and triple check the device references when creating
    partitions and file systems. Inattention to detail on that step can
    ruin your entire day. D.F.I.U.
3.  Be very careful when editing /etc/fstab. Errors in /etc/fstab will
    hang the machine.
4.  After completing the assignment, reboot the machine to make sure it boots cleanly and that your changes are permanent.
5.  Make sure that your accomplish the intended goal of freeing up space
    on the root drive of Machine E.
6.  Make sure that you do not change things like time stamps or file
    permissions in the home directories.
