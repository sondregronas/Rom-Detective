from tests import *

from rom_detective.rom_detective import RomDetective
from rom_detective.const import PLATFORMS


def test_load_config():
    rd = RomDetective()
    rd.load_config(f'{TEST_FILES_PATH}\\test_config\\config.cfg')
    assert rd.platforms
    assert 'target_folder_here' == rd.target_folder

    rd.save_config(f'{TEST_FILES_PATH}\\test_config\\config2.cfg')
    assert 'TARGET_FOLDER==target_folder_here\n' \
           'default:::n64:::C:\\' == open(f'{TEST_FILES_PATH}\\test_config\\config2.cfg', 'r', encoding='utf-8').read().strip()

    with pytest.raises(Warning):
        rd.load_config(f'{TEST_FILES_PATH}\\test_config\\empty_config.cfg')
