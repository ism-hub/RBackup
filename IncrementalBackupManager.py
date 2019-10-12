import datetime 
from pathlib import Path
import glob
import subprocess
import os
import RsyncCommandBuilder
import utils
import logging

class IncrementalBackupManager:
    def __init__(self, backupsFolder, backupsName, source, remote, logFile):
        self.backupFldr = backupsFolder
        self.name = backupsName
        self.remote = remote
        self.source = source
        self.logFile = logFile
        self.commandBuilder = RsyncCommandBuilder.RsyncCommandBuilder()
        self.logger = logging
        self.logger.basicConfig(level=logging.DEBUG, filename=logFile)


    # backups remote:source into backupsFolder/name.dd-mm-yy_HH-MM-SS
    # we call the callback with the command we want to execute, so the user will be able to change the default parameters
    def backup(self, callback = None):
        lnkDst = self.getLatest()
        command = self.commandBuilder.createIncrementalBackupCommand(source = self.remote+":"+self.source, dest = self.backupFldr, name = self.name, logFile=self.logFile, linkDest=lnkDst, exclude = "")
        self.commandCallback(command, callback)
        command.run()
        self.updateNameToComplete(command)
    
    # continue the latest incomplete
    # we call the callback with the command we want to execute, so the user will be able to change the default parameters
    def continueBackup(self, callback = None):
        continueBackupCallback = self.continueCallbackGenerator(callback)
        self.backup(continueBackupCallback)

    def continueCallbackGenerator(self, userCallBack):
        def inner(command):
            if userCallBack != None:
                userCallBack(command)
        return inner

    def restore(self, remote, callback = None):
        latestBackup = self.getLatest()
        command = self.commandBuilder.restoreBackup(remote = remote, dest = self.source, backup = latestBackup + "/", log = self.logFile)
        self.commandCallback(command, callback)
        command.run()
    
    def getAllBackups(self):
        return utils.getAllPattern(self.backupFldr + self.name + ".??-??-??_??-??-??")

    def getAllIncomplete(self):
        return utils.getAllPattern(self.backupFldr + self.name + ".??-??-??_??-??-??.incomplete")
    
    def getLatestIncomplete(self):
        folders = self.getAllIncomplete()
        if not bool(folders):
            return ""
        return max(folders, key=lambda folderPath: utils.getDatetimeFromString(folderPath.rsplit('.', 2)[1]))

    # returns the backup folder name with the latest backup
    def getLatest(self):
        folders = self.getAllBackups()
        if not bool(folders):
            return ""
        return max(folders, key=lambda folderPath: utils.getDatetimeFromString(folderPath.rsplit('.', 1)[1]))

    # getting rid of the '.incomplete' suffix
    def updateNameToComplete(self, command):
        completedName = command.getDestination().rsplit('.', 1)[0] 
        os.rename(command.getDestination(), completedName)
        self.logger.info("changed backup name from: " + command.getDestination() +" to: " + completedName)

    def commandCallback(self, command, callback):
        self.logger.info("Created the command: " + command.toString())
        if callback != None:
            callback(command)
            self.logger.info("After user callback, the command is: " + command.toString())
