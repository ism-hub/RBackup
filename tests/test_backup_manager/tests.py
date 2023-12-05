from IncrementalBackupManager import IncrementalBackupManager
import os
import glob
from os.path import exists
import shutil
from time import sleep
import backup_manager_config as conf
from importlib import reload

def test_files_in_link_dest_are_not_getting_deleted():
    # first backup
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    backup_manager.backup()

    # delete file_a and do second backup
    os.remove(f'{src_path_a}/file_a')

    sleep(1)  # to get different timestamps (exception otherwise)
    backup_manager.backup()

    # assert file_a doesn't exists in the second (latest) backup
    ordered_backups = backup_manager.get_all_completed_backups()
    assert len(ordered_backups)==2
    assert not exists(f"{ordered_backups[1]}{src_path_a}/file_a")

    # asssert file_a exists in the first backup
    fp = open(f'{ordered_backups[0]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content'
    fp.close()

def test_sanity():
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    backup_manager.backup()

    # assert we created the backupfile in the desired format
    backups = [f for f in glob.glob(backups_root_folder + '/' + backups_name_prefix + ".??-??-????_??-??-??")]
    assert len(backups) == 1  # only one backup is created and it is in the correct format
    assert  len([f for f in glob.glob(backups_root_folder + '/*')]) == 1  # nothig else, except the backup, was created.

    latest_backup_path = backups[0]
    fp = open(f'{latest_backup_path}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content'
    fp.close()
    # create file b
    fp = open(f'{latest_backup_path}{src_path_b}/file_b', 'r')
    assert fp.readline() == 'file b content'
    fp.close()

def test_files_in_link_dest_are_not_getting_changed_when_file_is_updated():
    # first backup
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    # first backup
    backup_manager.backup()

    # update file_a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content new')
    fp.close()

    # second backup
    sleep(1)  # so the backups will have different names (name is based on timestamp)
    backup_manager.backup()

    backups = backup_manager.get_all_completed_backups()
    # assert no changes to first backup
    fp = open(f'{backups[0]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content'
    fp.close()
    
    # assert second backup has the correct data
    fp = open(f'{backups[1]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content new'
    fp.close()

def test_files_in_link_dest_are_getting_hard_linked_when_not_changed():
    # first backup
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    # first backup
    backup_manager.backup()
    # make 3 backups last two hass no changes

    # update file_a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content new')
    fp.close()

    # second backup (only file_b should be hard-linked)
    sleep(1)  # so the backups will have different names (name is based on timestamp)
    backup_manager.backup()

    # third backup (everything should be hard-linked to the one before)
    sleep(1)  # so the backups will have different names (name is based on timestamp)
    backup_manager.backup()

    # assert hard-links
    backups = backup_manager.get_all_completed_backups()
    backup_0_file_a_inode = os.stat(f'{backups[0]}{src_path_a}/file_a').st_ino
    backup_1_file_a_inode = os.stat(f'{backups[1]}{src_path_a}/file_a').st_ino
    backup_2_file_a_inode = os.stat(f'{backups[2]}{src_path_a}/file_a').st_ino
    backup_0_file_b_inode = os.stat(f'{backups[0]}{src_path_b}/file_b').st_ino
    backup_1_file_b_inode = os.stat(f'{backups[1]}{src_path_b}/file_b').st_ino
    backup_2_file_b_inode = os.stat(f'{backups[2]}{src_path_b}/file_b').st_ino
    assert backup_0_file_a_inode != backup_1_file_a_inode and backup_0_file_a_inode != backup_2_file_a_inode
    assert backup_0_file_b_inode == backup_1_file_b_inode and backup_0_file_b_inode == backup_2_file_b_inode
    assert backup_1_file_a_inode == backup_2_file_a_inode

def test_we_cont_where_we_stopped_when_last_run_was_incomplete_and_date_changes():
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    # first backup
    backup_manager.backup()

    # change the backup manually to mock incomplete 
    backup = backup_manager.get_all_completed_backups()[0]
    os.rename(backup, f"{backup}.incomplete")
    # sanity that we have incomplete
    assert len(backup_manager.get_all_completed_backups()) == 0
    assert backup_manager.get_incomplete() is not None

    # update file_a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content new')
    fp.close()

    # second backup (should recognize incomplete and cont it)
    sleep(1)
    backup_manager.backup()

    backups = backup_manager.get_all_completed_backups()
    assert len(backups) == 1
    assert backup_manager.get_incomplete() is None
    # assert changes even tho incomplete had file without changes
    fp = open(f'{backups[0]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content new'
    fp.close()

def test_previous_backup_hard_link_not_getting_changed_when_incomplete():
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    # first backup
    backup_manager.backup()

    # second backup
    sleep(1)
    backup_manager.backup()

    # change the backup manually to mock incomplete 
    backup = backup_manager.get_all_completed_backups()[0]
    os.rename(backup, f"{backup}.incomplete")
    # sanity that we have incomplete
    assert len(backup_manager.get_all_completed_backups()) == 1
    assert backup_manager.get_incomplete() is not None

    # update file_a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content new')
    fp.close()

    # third backup
    sleep(1)
    backup_manager.backup()

    # sanity
    backups = backup_manager.get_all_completed_backups()
    assert backup_manager.get_incomplete() is None
    assert len(backups) == 2

    # assert hard-links
    backup_0_file_a_inode = os.stat(f'{backups[0]}{src_path_a}/file_a').st_ino
    backup_1_file_a_inode = os.stat(f'{backups[1]}{src_path_a}/file_a').st_ino
    backup_0_file_b_inode = os.stat(f'{backups[0]}{src_path_b}/file_b').st_ino
    backup_1_file_b_inode = os.stat(f'{backups[1]}{src_path_b}/file_b').st_ino
    assert backup_0_file_a_inode != backup_1_file_a_inode
    assert backup_0_file_b_inode == backup_1_file_b_inode

    # assert content
    fp = open(f'{backups[0]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content'
    fp.close()

    fp = open(f'{backups[1]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content new'
    fp.close()

    fp = open(f'{backups[1]}{src_path_b}/file_b', 'r')
    assert fp.readline() == 'file b content'
    fp.close()

def test_we_delete_files_when_cont_incomplete():
    src_path_a = '/RBackup/test_artifacts/src_folder/a'
    src_path_b = '/RBackup/test_artifacts/src_folder/b'
    backups_root_folder = '/RBackup/test_artifacts/backups_root_folder'
    backups_name_prefix = 'test_backup_prefix'

    # create backup-manger
    backup_manager = IncrementalBackupManager(backups_root_folder=backups_root_folder, backups_name_prefix=backups_name_prefix, src_paths=[src_path_a, src_path_b], remote_src_host=None)
    # create paths
    if not os.path.exists(src_path_b):
        os.makedirs(src_path_b)
    if not os.path.exists(src_path_a):
        os.makedirs(src_path_a)
    # create file a
    fp = open(f'{src_path_a}/file_a', 'w')
    fp.write('file a content')
    fp.close()
    # create file b
    fp = open(f'{src_path_b}/file_b', 'w')
    fp.write('file b content')
    fp.close()

    # first backup
    backup_manager.backup()

    # second backup
    sleep(1)
    backup_manager.backup()

    # change the backup manually to mock incomplete 
    backup = backup_manager.get_all_completed_backups()[0]
    os.rename(backup, f"{backup}.incomplete")

    # delete file_a
    os.remove(f'{src_path_a}/file_a')

    # third backup (cont. incomplete)
    sleep(1)
    backup_manager.backup()

    backups = backup_manager.get_all_completed_backups()
    assert not exists(f"{backups[1]}{src_path_a}/file_a")
    assert exists(f"{backups[0]}{src_path_a}/file_a")
    # assert content
    fp = open(f'{backups[0]}{src_path_a}/file_a', 'r')
    assert fp.readline() == 'file a content'
    fp.close()

def test_user_provided_params_overrides_default_ones():
    if os.environ.get("REAL_RUN","0") == "1":
        assert len(conf.get_backups_src_paths()) > 0, "ERROR: MUST set SRCS_TO_BACKUP"
        return

    # assert defaults
    assert conf.get_log_file() is None
    assert conf.get_rsync_dict_params() == {}
    assert conf.get_rsync_single_params() == ["-a", "-x", "-H", "--mkpath", "--progress" ,"--verbose", "--human-readable", "--numeric-ids", "--delete", "--relative", "--delete-excluded"]
    assert conf.get_remote_src_host() is None
    assert conf.get_backups_src_paths() == []
    assert conf.get_backups_root_folder() == '/backups'
    assert conf.get_backups_name_prefix() == 'my_backup'
    assert conf.get_minimum_hours_between_backups_guard() == 20
    assert conf.get_max_backups() == 30

    # change env and force reload
    os.environ["BACKUP_NAME_PREFIX"] = "test_prefix123"
    os.environ["SRCS_TO_BACKUP"] = "/src1,/src2222"
    os.environ["LOG_FILE"] = "log-file"
    os.environ["REMOTE_SRC_HOST"] = "remote-src"
    os.environ["RSYNC_SINGLE_PARAMS"] = "-x,-y,-z"
    os.environ["RSYNC_DICT_PARAMS"] = "{'key':'vall'}"
    os.environ['MAX_BACKUPS'] = '12'
    os.environ['MINIMUM_TIME_GUARD_H'] = '6'

    reload(conf)

    # assert new values
    assert conf.get_log_file() == "log-file"
    assert conf.get_rsync_dict_params() == {'key':'vall'}
    assert conf.get_rsync_single_params() == ["-x","-y","-z"]
    assert conf.get_remote_src_host() == "remote-src"
    assert conf.get_backups_src_paths() == ["/src1","/src2222"]
    assert conf.get_backups_root_folder() == '/backups'
    assert conf.get_backups_name_prefix() == 'test_prefix123'
    assert conf.get_max_backups() == 12
    assert conf.get_minimum_hours_between_backups_guard() == 6

    # cleanup and reload again 
    os.environ.pop("BACKUP_NAME_PREFIX")
    os.environ.pop("SRCS_TO_BACKUP")
    os.environ.pop("LOG_FILE")
    os.environ.pop("REMOTE_SRC_HOST")
    os.environ.pop("RSYNC_SINGLE_PARAMS")
    os.environ.pop("RSYNC_DICT_PARAMS")
    os.environ.pop('MAX_BACKUPS')
    os.environ.pop('MINIMUM_TIME_GUARD_H')

    reload(conf)
