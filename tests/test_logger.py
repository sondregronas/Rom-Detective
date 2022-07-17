import pytest
import os

from pathlib import Path

from rom_detective.class_logger import Logger
from test_const import TEST_FILES_PATH


def test_logger():
    logger = Logger()

    assert logger.total == 0
    logger.add({'success': 'Test'})
    assert logger.total == 1
    assert logger.successful == 1
    logger.add({'blacklist': 'Test'})
    logger.add({'blacklist': 'Test'})
    assert logger.blacklisted == 2
    logger.add({'platforms': 'Test'})
    assert logger.platforms == 1
    assert logger.total == 3

    assert 'Log results:' in str(logger)


def test_logger_load_log():
    with pytest.raises(NotImplementedError):
        logger = Logger().load(f'{TEST_FILES_PATH}\\test.log')
        assert logger


@pytest.mark.createfiles(reason='Creates folders & files, use --create-files flag to run')
def test_logger_write():
    logger = Logger()
    logger.add({'success': 'Test'})
    assert not os.path.exists(f'{TEST_FILES_PATH}\\{logger.log_files["success"]}')
    logger.write(path_dir=f'{TEST_FILES_PATH}')
    assert os.path.exists(f'{TEST_FILES_PATH}\\{logger.log_files["success"]}')

    # Ensure logger can make 1 folder ("logs") if required
    assert not Path(f'{TEST_FILES_PATH}\\test_log_folder').exists()
    logger.write(path_dir=f'{TEST_FILES_PATH}\\test_log_folder')
    assert Path(f'{TEST_FILES_PATH}\\test_log_folder').exists()

    # Ensure logger can't make 2 folders
    with pytest.raises(RuntimeError):
        logger.write(path_dir=f'{TEST_FILES_PATH}\\test_log_folder2\\nested')


def test_logger_write_dryrun():
    logger = Logger()
    logger.add({'dry_run': 'Test'})
    assert not logger.write(path_dir=f'{TEST_FILES_PATH}')
