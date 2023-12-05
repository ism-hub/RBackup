import os
from typing import Dict, List, Optional

# Rsync configuratoin
# don't use --inplace as this can change files from previous backups (to further understand why can add '--inplace' and run the tests to see the fail)
default_rsync_configuration_single_params = ["-a", "-x", "-H", "--mkpath", "--progress" ,"--verbose", "--human-readable", "--numeric-ids", "--delete", "--relative", "--delete-excluded"]

# notice --log-file is taken from the LOG_FILE env variable and no need to specify here (no log-file in env variable means stdout)
default_rsync_configuration_dict_params = {} #{"--log-file" : self.log_file}

# Backup Manager configuration
backups_root_folder = os.getenv('_BACKUPS_ROOT_FOLDER', '/backups')
backups_name_prefix = os.getenv('BACKUP_NAME_PREFIX', 'my_backup')
src_paths = os.environ.get('SRCS_TO_BACKUP').split(',') if os.environ.get('SRCS_TO_BACKUP') is not None else []  # comma seperated paths e.g. "/home/uname/.config, /root/bin". this is a must and will throw if remains empty list (not throwing here as we fill it in tests)
log_file = os.environ.get('LOG_FILE')  # None means stdout 
remote_src_host = os.environ.get('REMOTE_SRC_HOST')  # None means the src is local, format uname@<ip/domain>[:port] for ssh
max_backups = int(os.getenv('MAX_BACKUPS', '30'))  # default is 30. when 30 is reached it deletes the oldest one before creating a new one

# Default is 20. if for some reason asking for backup before this time passed - don't do anything.
# Always continue incomplete backups (regardless of passed time)
# This param is useful if the backup keep faling so you can just set the crontab to be called every few mins and it will try to cont the failed (incomplete) backup (but won't create a new backup if one already succeeded not far ago)
minimum_hours_between_backups_guard = int(os.getenv('MINIMUM_TIME_GUARD_H', '20'))  

# override rsync-single-params if user specified env var
# format is comma seperated string e.g. '-a,-X-,--relative'
rsync_user_provided_single_params = os.environ.get('RSYNC_SINGLE_PARAMS')
if rsync_user_provided_single_params is not None:
    default_rsync_configuration_single_params = rsync_user_provided_single_params.split(',')

# override rsync-dict-params if user specified env var
# format should be a valid json string e.g. '{"--log-file": "/.."}'
rsync_user_provided_dict_params = os.environ.get('RSYNC_DICT_PARAMS')
if rsync_user_provided_dict_params is not None:
    default_rsync_configuration_dict_params = eval(rsync_user_provided_dict_params) 

def get_rsync_single_params() -> List:
    return default_rsync_configuration_single_params

def get_rsync_dict_params() -> Dict[str, str]:
    return default_rsync_configuration_dict_params

def get_backups_root_folder() -> str:
    return backups_root_folder

def get_backups_name_prefix() -> str:
    return backups_name_prefix

def get_backups_src_paths() -> List[str]:
    return src_paths

# None means stdout
def get_log_file() -> Optional[str]:
    return log_file

# None means local
def get_remote_src_host() -> Optional[str]:
    return remote_src_host

def get_max_backups() -> int:
    return max_backups

def get_minimum_hours_between_backups_guard() -> int:
    return minimum_hours_between_backups_guard
