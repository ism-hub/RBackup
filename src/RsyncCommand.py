import datetime 
from pathlib import Path
import glob
import subprocess
import os
from dataclasses import dataclass
from typing import List, Dict, Optional

class RsyncCommand:

    def __init__(self, srcs: List[str], src_port: Optional[int], dst: str, single_params: List[str] = [], dict_params: Dict[str, str] = {}):
        self._srcs: List[str] = srcs
        assert len(self._srcs)
        self._dst: str = dst
        self._single_params: List[str] = single_params
        self._params_map: Dict[str, str] = dict_params
        self.src_port: Optional[int] = src_port

    def to_string(self):
        rsync_command = "rsync " + " ".join(self._single_params) 
        if self.src_port is not None:
            rsync_command = rsync_command + f' -e"ssh -p{self.src_port}"'
        rsync_command = rsync_command + " " + " ".join([(param + "=" + self._params_map[param]) for param in self._params_map])
        rsync_command = rsync_command + " " + " ".join(self._srcs) + " " + self._dst
        return rsync_command

    """
    Executing the rsync command, will throw on fail (check=True)
    """
    def run(self):
        rsync_command = self.to_string()
        #return subprocess.run(rsyncCommand.split(), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return subprocess.run(rsync_command, shell=True, universal_newlines=True, check=True)
