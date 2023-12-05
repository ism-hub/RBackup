from IncrementalBackupManager import IncrementalBackupManager
import backup_manager_config as conf
import sys
import logging
import utils
import datetime

logger = logging
if conf.get_log_file() is None:
    logger.basicConfig(level=logging.DEBUG, stream=sys.stdout)
else:
    logger.basicConfig(level=logging.DEBUG, filename=conf.get_log_file())

def get_backup_manager() -> IncrementalBackupManager:
    return IncrementalBackupManager(backups_root_folder=conf.get_backups_root_folder(), backups_name_prefix=conf.get_backups_name_prefix(), src_paths=conf.get_backups_src_paths(), remote_src_host=conf.get_remote_src_host())

def main():
    logger.log(logger.INFO, "-------- Starting cron script --------")

    backup_manager = get_backup_manager()

    # Should we delete oldest backup (if we have too many)
    backups = backup_manager.get_all_completed_backups() 
    if len(backups) >= conf.get_max_backups():
        logger.log(logger.INFO, f"We save backup history of {conf.get_max_backups()}, if we have more we delte the oldest one")
        logger.log(logger.INFO, f"Currently we have {len(backups)} backups")
        oldest_backup = backups[0]
        logger.log(logger.INFO, f"---- Deleteing oldest backup {oldest_backup}")
        backup_manager.delete_backup(oldest_backup)

    # if under conf.get_minimum_hours_between_backups_guard hours have been passed dont create a new backup
    # if we have incomplete backup always continue it
    if backup_manager.get_incomplete() is None and len(backups) > 0:
        min_hours_guard = conf.get_minimum_hours_between_backups_guard()
        latest_backup = backups[-1]
        latest_backup_datetime = utils.pars_datetime_from_backup_folder_path(latest_backup)
        datetime_now = datetime.datetime.now(datetime.UTC)
        hours_from_last_run = divmod((datetime_now - latest_backup_datetime).total_seconds(), 3600)[0]
        if hours_from_last_run < min_hours_guard: # don't allow backup
            logger.log(logger.INFO, f"We allow only 1 backup per {min_hours_guard} hours")
            logger.log(logger.INFO, f"Latest backup is on {latest_backup_datetime} current time is {datetime_now} total of {hours_from_last_run} hours passed")
            logger.log(logger.INFO, f"Less than {min_hours_guard} hours have been passed, do nothing")
            logger.log(logger.INFO, "-------- Existing cron script --------")
            return 0

    # start backup
    if backup_manager.get_incomplete() is not None:
        logger.log(logger.INFO, f"---- Continueing incomplete backup {backup_manager.get_incomplete()}")
    elif len(backups) > 0:
        logger.log(logger.INFO, f"---- Creating new backup previous backup is {backups[-1]}")
    else:
        logger.log(logger.INFO, f"---- Creating new backup no previous backups found")

    backup_manager.backup()
    logger.log(logger.INFO, f"---- Done backing up, latest backup is {backup_manager.get_all_completed_backups()[-1]}")
    logger.log(logger.INFO, "-------- Existing cron script --------")

if __name__ == "__main__":
    main()
