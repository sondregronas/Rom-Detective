import pytest
import os

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
    assert logger.total == 4

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
    logger.write(path=f'{TEST_FILES_PATH}')
    assert os.path.exists(f'{TEST_FILES_PATH}\\{logger.log_files["success"]}')


def test_loger_write_dryrun():
    logger = Logger()
    logger.add({'dry_run': 'Test'})
    assert not os.path.exists(f'{TEST_FILES_PATH}\\{logger.log_files["success"]}')
    logger.write(path=f'{TEST_FILES_PATH}')
    assert not os.path.exists(f'{TEST_FILES_PATH}\\{logger.log_files["success"]}')
