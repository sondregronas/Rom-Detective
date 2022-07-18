import pytest

from tests import *

from rom_detective.rom_detective import RomDetective, RDFlag
from rom_detective.const import PLATFORMS
from rom_detective import initialize_folder


def test_simulate_user():
    rd = RomDetective()

    rd.add_rom_folder(TEST_ROMS_PATH)
    rd.add_steam_folder(f'{TEST_FILES_PATH}\\steam')

    assert PLATFORMS['n64'] in rd.platforms.values()
    assert not PLATFORMS['atari2600'] in rd.platforms.values()
    rd.specify_platform(f'{TEST_ROMS_PATH}\\n64', PLATFORMS['atari2600'])
    assert not PLATFORMS['n64'] in rd.platforms.values()
    assert PLATFORMS['atari2600'] in rd.platforms.values()

    rd.specify_platform(f'{TEST_ROMS_PATH}\\n64', PLATFORMS['n64'])
    assert PLATFORMS['n64'] in rd.platforms.values()
    assert not PLATFORMS['atari2600'] in rd.platforms.values()

    assert len(rd.platforms) == 5
    rd.remove_folder(f'{TEST_ROMS_PATH}\\n64')
    assert len(rd.platforms) == 4
    assert not PLATFORMS['n64'] in rd.platforms.values()


@pytest.mark.createfiles(reason='Creates folders & files, use --create-files flag to run')
def test_create_shortcuts():
    with pytest.raises(RuntimeError):
        initialize_folder(f'{TEST_FILES_PATH}\\test_startup')

    initialize_folder(f'{TEST_FILES_PATH}\\test_startup')

    rd = RomDetective()

    rd.add_rom_folder(TEST_ROMS_PATH)
    rd.add_steam_folder(f'{TEST_FILES_PATH}\\steam')

    rd.index_and_create_shortcuts()
    assert rd.logger.successful > 0
    assert rd.logger.blacklisted > 0
