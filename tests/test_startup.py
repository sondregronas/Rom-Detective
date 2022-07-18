import pytest

from pathlib import Path

from rom_detective.startup import init_folders
from test_const import TEST_FILES_PATH


@pytest.mark.createfiles(reason='Creates folders & files, use --create-files flag to run')
def test_init_folders():
    assert not Path(f'{TEST_FILES_PATH}\\test_startup\\logs').exists()
    assert init_folders(f'{TEST_FILES_PATH}\\test_startup')
    assert Path(f'{TEST_FILES_PATH}\\test_startup\\logs').exists()

    with pytest.raises(RuntimeError):
        init_folders(f'{TEST_FILES_PATH}\\test_startup_folderdoesnotexist')
