from time import sleep
import os
import logging
import sys
logger = logging
logger.basicConfig(level=logging.DEBUG, stream=sys.stdout)

def test_minimum_wait_guard_is_preventing_backups(cron_script, conf):
    # running the cron_script (should create 1 backup)
    cron_script.main()

    # assert we have 1 backup
    backup_manager = cron_script.get_backup_manager()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None
    backup_path = backup_manager.get_all_completed_backups()[0]

    # running the cron_script again, the time-guard should prevent another backup
    cron_script.main()
    backup_manager = cron_script.get_backup_manager()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None
    assert backup_path == backup_manager.get_all_completed_backups()[0]

    # set 0 in the minimum time guard so it will always accept
    origin_min_guard = conf.minimum_hours_between_backups_guard
    conf.minimum_hours_between_backups_guard = 0
    sleep(1)  # so we wont get the same timestamp (res of seconds)
    cron_script.main()
    # assert we created another backup
    assert len(backup_manager.get_all_completed_backups()) == 2
    assert backup_manager.get_incomplete() is None
    assert backup_path == backup_manager.get_all_completed_backups()[0]

    # restor original value
    conf.minimum_hours_between_backups_guard = origin_min_guard

def test_that_minimum_wait_guard_not_delaying_incomplete_backups_no_complete_backups(cron_script):
    # running cron script will create the first backup
    cron_script.main()
    backup_manager = cron_script.get_backup_manager()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None

    # sanity, running the cron_script again, the time-guard should prevent another backup
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None

    # mark this backup as incomplete
    backup_path = backup_manager.get_all_completed_backups()[0]
    os.rename(backup_path, f"{backup_path}.incomplete")
    assert len(backup_manager.get_all_completed_backups()) == 0
    assert backup_manager.get_incomplete() is not None

    # run the script again, and even tho the min hours havn't passed we will cont the incomplete backup
    cron_script.main()
    backup_manager = cron_script.get_backup_manager()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None

    # sanity, running the cron_script again, the time-guard should prevent another backup
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None

def test_that_minimum_wait_guard_not_delaying_incomplete_backups_we_also_have_previous_backups(cron_script, conf):
    # running the cron_script (should create 1 backup)
    cron_script.main()
    backup_manager = cron_script.get_backup_manager()

    # assert we have 1 backup
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None

    # set 0 in the minimum time guard so it will always accept
    origin_min_guard = conf.minimum_hours_between_backups_guard
    conf.minimum_hours_between_backups_guard = 0
    sleep(1)  # so we wont get the same timestamp (res of seconds)
    cron_script.main()
    # assert we created another backup
    assert len(backup_manager.get_all_completed_backups()) == 2
    assert backup_manager.get_incomplete() is None

    # restor original value
    conf.minimum_hours_between_backups_guard = origin_min_guard

    # mark the latest backup as incomplete
    backup_path = backup_manager.get_all_completed_backups()[1]
    os.rename(backup_path, f"{backup_path}.incomplete")
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is not None

    # run the script again, and even tho the min hours havn't passed we will cont the incomplete backup
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 2
    assert backup_manager.get_incomplete() is None

def test_we_delete_backups_after_we_have_max_num_of_them(cron_script, conf):
    backup_manager = cron_script.get_backup_manager()
    # set 0 in the minimum time guard so we will always create new backups
    origin_min_guard = conf.minimum_hours_between_backups_guard
    conf.minimum_hours_between_backups_guard = 0

    # set the maximum number of backups to 3
    origin_max_backups = conf.max_backups
    conf.max_backups = 3
    
    # create first backup
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is None
    first_backup = backup_manager.get_all_completed_backups()[0]

    # create second backup
    sleep(1)  # so backups will have different timestamps
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 2
    assert backup_manager.get_incomplete() is None
    assert first_backup in backup_manager.get_all_completed_backups()

    # create third backup
    sleep(1)  # so backups will have different timestamps
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 3
    assert backup_manager.get_incomplete() is None
    assert first_backup in backup_manager.get_all_completed_backups()

    # create fourth backup, the max-backups should dleted the oldest one backup
    sleep(1)  # so backups will have different timestamps
    cron_script.main()
    assert len(backup_manager.get_all_completed_backups()) == 3
    assert backup_manager.get_incomplete() is None
    assert first_backup not in backup_manager.get_all_completed_backups()

    # restor original conf values
    conf.minimum_hours_between_backups_guard = origin_min_guard
    conf.max_backups = origin_max_backups
    pass
