import shutil
import pytest

@pytest.fixture(scope='function', autouse=True)
def cleanup():
    shutil.rmtree("/RBackup/test_artifacts", ignore_errors=True)
