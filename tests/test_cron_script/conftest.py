import pytest
import os
import shutil

@pytest.fixture(scope='session')
def cron_script():
    # set env variables
    os.environ["BACKUP_NAME_PREFIX"] = "cron_script_test"
    os.environ["SRCS_TO_BACKUP"] = "/RBackup/test_artifacts/src_folder/a,/RBackup/test_artifacts/src_folder/b"
    os.environ["_BACKUPS_ROOT_FOLDER"] = "/RBackup/test_artifacts/backups_root_folder"
    # os.environ["LOG_FILE"] = "log-file"
    # os.environ["REMOTE_SRC_HOST"] = "remote-src"
    # os.environ["RSYNC_SINGLE_PARAMS"] = "-x,-y,-z"
    # os.environ["RSYNC_DICT_PARAMS"] = "{'key':'vall'}"
    # os.environ['MAX_BACKUPS'] = '12'
    # os.environ['MINIMUM_TIME_GUARD_H'] = '6'
    import cron_script
    yield cron_script

@pytest.fixture(scope='session')
def conf(cron_script):
    import backup_manager_config
    yield backup_manager_config

@pytest.fixture(scope='function', autouse=True)
def cleanup():
    shutil.rmtree("/RBackup/test_artifacts", ignore_errors=True)

@pytest.fixture(autouse=True, scope="function")
def create_src_data(cleanup):
    # create src data
    src_path_a = "/RBackup/test_artifacts/src_folder/a"
    src_path_b = "/RBackup/test_artifacts/src_folder/b"
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

