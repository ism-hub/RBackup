import datetime 
import RsyncCommand

class RsyncCommandBuilder:

    #def __init__(self):

    def defaultBackupCommand(self, source, dest, logFile, linkDest="", exclude = ""):
        command = RsyncCommand.RsyncCommand(source, dest)
        command.addParamsSingle(["-a", "-x", "-H", "-A", "-X", "--progress" ,"--verbose", "--human-readable", "--inplace", "--numeric-ids", "--delete", "--delete-excluded"])#no -z (zipp) cuz the CPU on the server got too hot
        command.setParam("--log-file", logFile)
        if exclude != "":
             command.setParam("--exclude-from", exclude)
        if linkDest != "":
            command.setParam("--link-dest", linkDest)
        return command
       
     # @PRE: be sure the <name>.current is a valid link (just make sure to run backupManager.fixCurrentIfNeeded() if you are not sure)
    def createIncrementalBackupCommand(self, source, dest, name, logFile, linkDest = "", exclude = ""):
        if dest[-1:] != '/':
            raise ValueError("dest (" + dest + ") must end with a '/' ")
        backupPath = dest + name + "." + datetime.datetime.utcnow().strftime("%d-%m-%y_%H-%M-%S") + ".incomplete"
        return self.defaultBackupCommand(source=source, dest=backupPath, logFile=logFile, linkDest=linkDest, exclude=exclude)

    def restoreBackup(self, remote, dest, backup, log):
        #if dest[-1:] != '/':
        #    raise ValueError("dest (" + dest + ") must end with a '/' ")
        command = RsyncCommand.RsyncCommand(backup, remote+":"+dest)
        command.addParamsSingle(["-a", "-z", "-x", "-H", "-A", "-X", "--progress" ,"--verbose", "--human-readable", "--inplace", "--numeric-ids", "--update"])
        command.setParam("--log-file", log)
        return command