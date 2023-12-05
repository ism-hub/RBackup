import datetime 
from pathlib import Path
import glob
import subprocess
import os
from RsyncCommand import RsyncCommand
import utils
from typing import Optional, List
from functools import cmp_to_key
import backup_manager_config as conf
import shutil
import logging
import sys

logger = logging
if conf.get_log_file() is None:
    logger.basicConfig(level=logging.DEBUG, stream=sys.stdout)
else:
    logger.basicConfig(level=logging.DEBUG, filename=conf.get_log_file())

class IncrementalBackupManager:
    """
    Our backups are of the form <backups_root_folder>/<backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>/< src_path folder and its content>
    The backup process can take time, while in middle of backup (when rsync transfering files) the backup folder has '.incomplete' suffix
    i.e. <backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>.incomplete

    remote_src_host: if our source is the remote machine (rsync running on the destination machine and backing up the data from the remote_src_host)

    both remote_src/dst_host are optional and if 'None' assume local.

    src_paths: list of source-paths,
               this will result in <backups_root_folder>/<backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>/<full-path-of-source-path>
               notice: all the sources in stc_path share the same backup folder <backups_root_folder>/<backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>
    """
    def __init__(self, backups_root_folder: str, backups_name_prefix: str, src_paths: List[str], remote_src_host: Optional[str] = None):
        self.backups_root_folder: str = backups_root_folder.rstrip('//')
        self.backups_name_prefix: str = backups_name_prefix
        assert '.' not in backups_name_prefix and '/' not in backups_name_prefix, "backups_name_prefix can't contains '.' or '/'"
        self.remote_src_host: Optional[str] = remote_src_host 
        self.src_paths: List[str] = src_paths

    """
    Creates a backup
    If there is an incomplete backup, continues it.
    """
    def backup(self) -> None:
        if self.has_incomplete_backup():
            self._continue_incomplete_backup()
        else:
            self._create_new_backup()

    """
    Checks to see if we have file with the form of -
    <backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>.incomplete
    """
    def has_incomplete_backup(self) -> bool:
        return self.get_incomplete() is not None

    """
    Created new backup, ignores if we have incomplete one.
    Backup is based-on (hard-linked againts) the latest previous backup.
    """
    def _create_new_backup(self) -> None:
        latest_backup_path = self.get_latest_backup_path()

        # create rsync command and run
        # create new backup.incomplete folder name
        incomplete_backup_name = self.backups_name_prefix + '.' + datetime.datetime.now(datetime.UTC).strftime("%d-%m-%Y_%H-%M-%S") + '.incomplete' # utils.generate_incomplete_backup_name(backups_name_prefix=self.backups_name_prefix) # e.g. <backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>.incomplete
        # calculate host 
        src_hostname = None
        src_port = None
        if self.remote_src_host is not None:
            src_hostname, src_port = utils.get_source_name_and_port_from_full_hostname(self.remote_src_host)
        full_srcs = [(src_hostname + ":" if src_hostname else "") + src for src in self.src_paths]  # e.g. uname@server-name:/<stuff I want to backup>...
        full_dst = self.backups_root_folder + '/' + incomplete_backup_name

        # create rsync command
        rsync_dict_params = conf.get_rsync_dict_params().copy()
        if conf.get_log_file() is not None:
            rsync_dict_params["--log-file"] = conf.get_log_file()
        if latest_backup_path is not None:
            rsync_dict_params["--link-dest"] = latest_backup_path

        backup_rsync_command = RsyncCommand(srcs=full_srcs, src_port=src_port, dst=full_dst, single_params=conf.get_rsync_single_params(), dict_params=rsync_dict_params)
        backup_rsync_command.run()  # will throw on fail

        # ----- backup completed successfully -----

        # mark the backup as completed (by removing the '.incomplete' from its name)
        complete_backup_name = incomplete_backup_name.rsplit(".", 1)[0] # utils.get_complete_backup_name_from_incomplete_name(incomplete_backup_name) # basically remoues the `.incomplete` from the name
        incomplete_backup_path = self.backups_root_folder + '/' + incomplete_backup_name
        complete_backup_path = self.backups_root_folder + '/' + complete_backup_name

        os.rename(incomplete_backup_path, complete_backup_path)  # dst is local

    """
    Continue the last incomplete backup.
    After done - change the timestamp of the folder to reflect a newer backup (the timestamp in the folder name).
    """
    def _continue_incomplete_backup(self) -> None:
        assert self.has_incomplete_backup(), "there is no incomplete backup to continue (no .incomplete folder)"
        incomplete_backup_path = self.get_incomplete()
        logger.log(logger.INFO, f"Continuing incomplete backup {incomplete_backup_path}")

        # cont incomplete backup
        # create rsync command
        src_hostname = None
        src_port = None
        if self.remote_src_host is not None:
            src_hostname, src_port = utils.get_source_name_and_port_from_full_hostname(self.remote_src_host)
        full_srcs = [(src_hostname + ":" if src_hostname else "") + src for src in self.src_paths]  # e.g. uname@server-name:/<stuff I want to backup>...
        full_dst = incomplete_backup_path  # giving it the existing incomplete as dst

        rsync_dict_params = conf.get_rsync_dict_params().copy()
        if conf.get_log_file() is not None:
            rsync_dict_params["--log-file"] = conf.get_log_file()
        latest_backup_path = self.get_latest_backup_path()
        if latest_backup_path is not None:
            rsync_dict_params["--link-dest"] = latest_backup_path

        backup_rsync_command = RsyncCommand(srcs=full_srcs, src_port=src_port, dst=full_dst, single_params=conf.get_rsync_single_params(), dict_params=rsync_dict_params)
        backup_rsync_command.run()  # will throw on fail

        # ----- backup completed successfully -----

        # change the backup folder name to reflect that it is no longer '.incomplete' and the new time
        # create new backup folder name (with newer timestamp)
        complete_backup_new_name = self.backups_name_prefix + '.' + datetime.datetime.now(datetime.UTC).strftime("%d-%m-%Y_%H-%M-%S")
        complete_backup_new_path = self.backups_root_folder + '/' + complete_backup_new_name 

        os.rename(incomplete_backup_path, complete_backup_new_path)

    # """
    # Restores the latest backup back to source
    # TODO
    # """
    # def restore(self, remote):
    #     latestBackup = self.get_latest_backup_path()
    #     command = self.commandBuilder.restoreBackup(remote = remote, dest = self.src_paths, backup = latestBackup + "/", log = self.log_file)
    #     self.commandCallback(command, callback)
    #     command.run()

    """
    Returns an ordered list of completed backups 
    (full paths of the backup, list with paths of the form <backups_root_folder>/<backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s> ).
    Latest backup is in the last index.
    """
    def get_all_completed_backups(self) -> List[str]:
        completed_backups = [f for f in glob.glob(self.backups_root_folder + '/' + self.backups_name_prefix + ".??-??-????_??-??-??")] 
        def compare(path1, path2):
            datetime1 = utils.pars_datetime_from_backup_folder_path(path1)
            datetime2 = utils.pars_datetime_from_backup_folder_path(path2)
            if datetime1 < datetime2:
                return -1
            elif datetime1 > datetime2:
                return 1
            else:
                return 0 
        return sorted(completed_backups, key=cmp_to_key(compare))

    """
    Gets incomplete of the form - <backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s>.incomplete if any
    notice: if you are using only one IncrementalBackupManager at a time there shouldn't be nultiple .incomplete or a backup which is greater than existing .incomplete
            I deliberately chose not to handle such cases to try and keep the code very simple.
    """
    def get_incomplete(self) -> Optional[str]:
        incompletes = [f for f in glob.glob(self.backups_root_folder + '/' + self.backups_name_prefix + ".??-??-????_??-??-??.incomplete")]
        if len(incompletes) > 0:
            assert len(incompletes) == 1
            return incompletes[0]
        else:
            return None

    """
    Returns the latest backup folder path
    (.../<backups_name_prefix>.<dd>-<mm>-<yyyy>_<h>-<m>-<s> with the most recent date <dd>-<mm>-<yy>_<h>-<m>-<s>)
    """
    def get_latest_backup_path(self) -> Optional[str]:
        completed_backups = self.get_all_completed_backups()
        if not bool(completed_backups): # if empty
            return None
        return completed_backups[-1]

    """
    Deletes the bakcup folder.
    """
    def delete_backup(self, backup_path: str) -> None:
        assert self.backups_root_folder in backup_path
        assert self.backups_name_prefix in backup_path
        shutil.rmtree(backup_path, ignore_errors=True)
