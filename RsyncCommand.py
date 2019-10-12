import datetime 
from pathlib import Path
import glob
import subprocess
import os

class RsyncCommand:

    def __init__(self, src, dst, singleParams = [], paramsMap = {}):
        self.src = src
        self.dst = dst
        self.singleParams = singleParams
        self.paramsMap = paramsMap

    def toString(self):
        rsyncCommand = "rsync " + " ".join(self.singleParams) 
        rsyncCommand = rsyncCommand + " " + " ".join([(param + "=" + self.paramsMap[param]) for param in self.paramsMap])
        rsyncCommand = rsyncCommand + " " + self.src + " " + self.dst
        return rsyncCommand

    def run(self):
        rsyncCommand = self.toString()
        #return subprocess.run(rsyncCommand.split(), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return subprocess.run(rsyncCommand.split(), universal_newlines=True, check=True)

    def getDestination(self):
        return self.dst

    def getSource(self):
        return self.src

    def isParamExist(self, param):
        return (param in self.paramsMap) or (param in self.singleParams)

    def getParamsValue(self, param):
        return self.paramsMap[param]

    def setParam(self, param, value):
        self.paramsMap[param] = value

    def addParamSingle(self, param):
        self.singleParams.append(param)

    def addParamsSingle(self, params):
        self.singleParams.extend(params)
