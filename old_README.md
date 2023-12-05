# How I do my backups 
- Users can upload/sync to/from a server (using samba and nextcloud).
- Once a day other computer (my desktop in my case (can be another server)) connects to the server and incrementally backs up the data on the server (on a backup drive that connected to the computer) using rsync.

# How the backups are organized 
Theme output - 
```
ism@ismain:/media/ism/WDBlue/backups$ ls -l
total 24
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.07-10-19_13-32-58
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.07-10-19_21-08-09
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.08-10-19_21-06-31
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.09-10-19_21-07-01
drwxr-xr-x+ 3 root root 4096 Oct  6 12:03 server.11-10-19_06-55-33
drwxr-xr-x+ 3 root root 4096 Oct 12 13:23 server.12-10-19_10-26-22
```
- *server.07-10-19_13-32-58* means we backed-up the server at Oct-7-2019,13:32:58 UTC time.

# Incomplete backups
We want to point out that a backup is still in progress or failed, hence incomplete, we do it by adding *'.incomplete'* to the end of the backup folder, for example before the *server.07-10-19_21-08-09* backup completed it was 
```
drwxr-xr-x 3 ism ism 4096 Oct  3 20:12 server.07-10-19_21-08-09.incomplete
```
Upon comletion we changed it to *server.07-10-19_21-08-09* 

# About incremental backups
 
Using the *--link-dest* option in rsync we can tell it to hard-link files which didn’t get changed (instead of copying them again), this way we don't pay in space for files that haven't been changed.

```
ism@ismain:/media/ism/WDBlue/backups$ sudo du -h --max-depth=1 | sort -hr
35G	./server.08-10-19_21-06-31
35G	.
261M	./server.07-10-19_21-08-09
50M	./server.09-10-19_21-07-01
28M	./server.12-10-19_10-26-22
25M	./server.11-10-19_06-55-33
336K	./server.07-10-19_13-32-58
```
These backups are roughly on the same files (all the backup folders have almost exactly the same files), as you can see only the first folder taking full space, the rest are just hardlinks. Lets delete the folder that takes all the space and see what will happen - 
```
ism@ismain:/media/ism/WDBlue/backups$ sudo rm -r ./server.08-10-19_21-06-31
ism@ismain:/media/ism/WDBlue/backups$ sudo du -h --max-depth=1 | sort -hr
35G	.
21G	./server.09-10-19_21-07-01
15G	./server.07-10-19_21-08-09
28M	./server.12-10-19_10-26-22
25M	./server.11-10-19_06-55-33
336K	./server.07-10-19_13-32-58
```
We can see that the folder (.) still takes 35G even after we deleted the one that showed to contain all the 35G (the backups are roughly on the same files so that isn’t a surprise).As expected we didn't lose the data (hard links).

# Standart for backups
- I'm trying to follow the [3-2-1-backup-strategy](www.backblaze.com/blog/the-3-2-1-backup-strategy/) from backblaze. (Currently I have only two that on-site)
- On top of that I want protection from accidental deletions, that is why the incremental backups. Now a question arises - how many backups do the incremental backups need?

# Why one of my backup drives is connected to my desktop instead the server
This way I can use the free space on the drive, after the backups, for myself, moreover I can use read only access on the data there (without using samba (samba can be slow over the network even in LAN for me) or syncing the folder with NextCloud (will gobble-up space)).

# Setup
## Server setup - Setting permissions and the backup user
As I mentioned the desktop, using rsync, connects to the server and incrementally backup the content on the server to itself (to the hdd on the desktop).

To be able to access all the files on the server without needing a root user I created a *backupsuser* user on the server 
```
sudo adduser backupsuser
```
And gave that user, using ACL, read-execute access to the *content* folder (and subfolders) on the server.
```
sudo setfacl -Rm u:backupuser:rx contentFolderPath
```
- **setfacl** - means *set file access list*.
- **-R** - *recursive*, meaning it will run the command on all the files, sub-folders (and the sub-folders files etc.).
- **-m** - *modify*, means to modify the current ACL, without it the command will delete the old access list and create a new one.
- **u:backupuser:rx** -
    - **u** - means we want to add a user rule to the ACL.
    - **backupuser** - the actual user we adding.
    - **rx** - we want him to have read/execute permissions to the file/folder (if you wondering why execute permission read [this](https://askubuntu.com/questions/660502/why-do-i-need-the-x-permission-to-cd-into-a-directory)).

To see the ACL we can use the *getfacl* command -
```
getfacl someFolder
```
my output before running the command - 
```
$ getfacl content/
# file: content/
# owner: ism
# group: ism
user::rwx
group::r-x
other::r-x
```
after -
```
$ getfacl content/
# file: content/
# owner: ism
# group: ism
user::rwx
user:backupsuser:r-x
group::r-x
mask::r-x
other::r-x
```
I do not want to run this command every time a user adds a file/folder to one of the folders in *content* (or its subfolders), the file/folder he adds should inherit the ACL from his parent directory. To do that I used this command - 
```
sudo setfacl -Rm d:u:backupuser:rx contentFolderPath
```
It is the same as before except the additional ***d***, it stands for *default*, we set a default ACL to the directories, meaning when someone is creating a file/directory in them he will inherit the ACL in the default section of the ACL of th directory. Here how the ACL looks like now -
```
$ getfacl content/
# file: content/
# owner: ism
# group: ism
user::rwx
user:backupuser:r-x
group::r-x
mask::r-x
other::r-x
default:user::rwx
default:user:backupuser:r-x
default:group::r-x
default:mask::r-x
default:other::r-x
```
It added a default ACL, now every time we add a file we will inherit the ACL according to the default section in the directory ACL (files doesn’t have *default* section in their ACL), and every time we create a directory we will inherit the ACL and the default-ACL entries. ([check this for more info](https://access.redhat.com/documentation/en-US/Red_Hat_Storage/2.0/html/Administration_Guide/ch09s05.html))

### Reset ACL changes
If you do not happy with your ACL changes and want to reset them, you can run - 
```
sudo setfacl -bn folderPath
```
Add the R (-Rbn) for recursive, taken from [here](https://unix.stackexchange.com/questions/339765/how-to-remove-acl-from-a-directory-and-back-to-usual-access-control).

## Desktop setup 
### Creating the script

Download the script files (clone the repository) -
```
git clone https://github.com/ism-hub/RBackup.git
```
Edit backup.py (supposed to act as a CLI to the code) with your parameters 

- **backupsFolder** - the folder to put your incremental backups, I put mine in /media/WDBLUE/backups/ (meaning in a folders named 'backups'  inside one of my drives) (this where the *\<name\>.03_10_19-17_14* folders will be)
- **backupsName** - the name of what we are backing up, I put 'server' in mine cause I'm backing up my server. (This will create the ***server**.03_10_19-17_14* folders)
- **logFile** - where you want the log file to be (can be './log' to put it in the script folder).
- **source** - we want the manager to backup a remote directory to this computer (to backupsFolder directory in this computer)
- **remote** - the server's address and user, i.e. 'backupuser@192.168.1.2'

# Doing the actual backup
### Running the script 
The backup script should run as root (we keep the original file owners of our remote source, meaning we will create files with different owner,groups,etc. control, a user can't create a file and transfer the ownership to another user, thats why we need the root)

### Backup

To backup type- 
```
sudo python3 backup.py --backup
```
This will create a folder  *backupsFolder*/*backupsName*.dd-mm-yyyy_hh-mm-ss.incomplete and start backing-up the *source* from *remote*, after the backup completed it removes the *.incomplete* from the folder

### Resume a backup

To continue the latest incomplete backup -
```
sudo python3 backup.py --continue
```
This will continue to backup the latest ...*.incomplete* we have in *backupsFolder*

### Restore a backup
There are two ways,
1. The simple way (but losing permissions) is to just open the backup folder in the server and grab the files you need.
2. Letting the desktop temporary root access to the server so we could restore the files with their permissions etc.

To restore a backup via method 2 run (after changing the server's authorized_keys file to allow the desktop to access the server as root (see below how))- 
```
sudo python3 backup.py --restore
```

### Getting an email upon errors 
The script try to send you an email upon crush, you will need to do a little procedure to let yagmail use your mail without a password, I'm using a gmail account specific for this purpose, this way you don't need to risk your main account.

# Automating the proccess
1. Not entering the remote (backupuser on the server) password (public key).
2. Not running the command ('sudo python3 backup.py') manually every time we want to backup. (Anacron)

## Connecting without password 
### Generate private key for the root on the desktop
Enter the following commands in the desktop (leave all empty (press enter) when the *ssh-keygen* asks you stuff)
```
sudo su -
ssh-keygen -b 4096
```
### Publishing the public key to the server's backups user
Now we need to give our public key to the server, we will open it with a text editor copy it and past it in *~/.ssh/authorized_keys* in the server. Install xclip in the desktop
```
apt get xclip
```
copy the public key (after the command if you do *rightclick -> past* you will see the key)
```
cat ~/.ssh/id_rsa.pub | xclip -selection clipboard
```
got to the server and add it to the *backupuser* authorized_keys: In the server type -

login as the backupuser
```
sudo su - backupuser
```
Open the *authorized_keys* file (if you dont have one you can just create it)
```
nano ~/.ssh/authorized_keys
```
Now past (you suppose to have the *id_rsa.pub* content on your clipboard, if you have something else run *cat ~/.ssh/id_rsa.pub | xclip -selection clipboard* on the desktop again) the public key in a new line.
press Ctrl+O, Ctrl+X to save and exit
```
Ctrl+O
Enter
Ctrl+x
```
Restart ssh service in the server
```
sudo service ssh restart
```
### Testing
Now you should be able to connect to the server's *backupuser* without password, to check it type- 
```
sudo ssh backupuser@yourserverip
```
### Security
Now that we can access to the server's backup user without password we don't need the *login* feature, lets disable it with - 
```
sudo passwd -l backupuser
```
We can see what our change did with - 
```
sudo passwd --status backupuser
```
My output - 
```
backupuser L ...
```
The **L** means *locked* (before the command it was **P**, meaning *password* protected), we still can connect with the private key, but we cannot connect with a password anymore.

to undo (unlock) the user type - 
```
sudo passwd -u backupuser
```
Try to connect again to see if everything still works.

## Anacron-job
To run the script once a day do -

create a serverbackup script inside /etc/cron.daily/
```
sudo nano /etc/cron.daily/serverbackup
```
With the line
```
#!/bin/sh
sudo python3 /root/backupscripts/backup.py --backup > /root/backupscripts/progress.txt
```
(while the backup is running you can see the progress in the progress.txt file)

# Program API


## Why the Desktop asking the server to back up the server files?
Instead of the server connecting to the desktop to back up its own (the server's) files? There are two main reasons:
1. Because the desktop is not up all the time and the server is, so instead of the server polling, the desktop can initiate.
2. In order to put files/folders that not belong to you (we save the original uid and gid of the server so they won't belong to the the user that rsync connects to) you need to be root, meaning the server will have root access to the desktop (probably via public key) and I didn't want it.([run-rsync-with-root-permission-on-remote-machine](https://superuser.com/questions/270911/run-rsync-with-root-permission-on-remote-machine))



# TODO
- better control on the command that runs (let the user see it and change it )
- handle incomplete backups (for now it just ignores them, it won't affect the next backup)
- Adding another drive for offsite backups (see *Plans for third drive below*).
- GUI to restore files, delete old backups, see which files are backed up in which drives and which are pending, etc.
- chroot jail for the backup user? ([source](https://blog.toonormal.com/2017/04/01/notes-creating-an-rsync-jail/))
- compressed incremental backups?


# Plans for third drive
- I want it to be in parents’ house and act as another server only for them (this way they will not need to connect to me when they have all their data on their LAN). I think the solution will be: 
    - For folders we both share and both need write access to (I do not think we have such) the data on their server and mine will be synced. (And the backup will be taken from my server). (Simple to achieve), 
        - Caveat: my server will backup the data back to them so they will end up with two copies of the same thing (plus the incremental updates).
            - Possible solution: not to do incremental updates for this data on their server, only do it for the desktop drive. (so we have 3 copies of the data, 2 synced and 1 incremental (on event of disk failure we are fine, on even of accidently deleting stuff not so much (only 1 backup of the history)))
    - For folders that I don't need or only need read access to (e.g. family photos) will be on their server (and I will be using their backups on my server (with read-only access)) (little-bit tricky permission wise, the backups are with their uid and gid)




