import IncrementalBackupManager
import sys
import yagmail
import datetime

backupsFolder = "/media/ism/WDBlue/backups/"
backupsName = "server"
logFile = "/root/backupscripts/rlog.txt"
source = "/media/usbhdd/synced/"
remote="backupuser@192.168.14.201"

#backupsFolder = "/media/ism/WDBlue/backups2/"
#backupsName = "server2"
#logFile = "/media/ism/WDBlue/backups2/rlog.txt"
#source = "/media/usbhdd/synced/testss/"
#remote="backupuser@192.168.14.201"

def log(msg):
    txt = datetime.datetime.utcnow().strftime("%d/%m/%y  %H:%M:%S ") + msg
    with open (logFile, 'a') as f: f.write (txt + '\n')
    #print(txt)

try:
    backupManager = IncrementalBackupManager.IncrementalBackupManager(backupsFolder = backupsFolder, backupsName = backupsName, logFile = logFile, source = source, remote=remote)

    if sys.argv[1] == '--backup':
        backupManager.backup()
    elif sys.argv[1] == '--restore':#dont forget to enable the publix key in the autorized_keys file
        backupManager.restore(remote = "root@192.168.14.201")
    elif sys.argv[1] == '--continue':
        backupManager.continueBackup()
    else:
        raise ValueError("(MINE ERROR) backup.py can be called with --backup or --restore --continue arguments only")
except Exception as ex:
    txt = "Excecption! when running the backup command: " + str(ex)
    log(txt)
    yag = yagmail.SMTP("yourmail@gmail.com", oauth2_file="~/oauth2_creds.json")
    contents = [txt, logFile]
    yag.send('ppersontwo@gmail.com', 'Backup FAIL!', contents)
    raise
