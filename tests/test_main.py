from rom_detective.util_main import (
    identify_platform_from_path,
    identify_platforms_from_path,
    index_roms_from_dict
)

from test_const import TEST_ROMS_PATH


def test_util_main():
    rom_folders = identify_platforms_from_path(TEST_ROMS_PATH)
    assert len(rom_folders) == 4

    games = index_roms_from_dict(rom_folders)
    assert len(games) == 16

    rom_folders.update({f'{TEST_ROMS_PATH}\\n64': None})
    games = index_roms_from_dict(rom_folders)
    assert len(games) == 13


def test_identify_platform_exception(capfd):
    identify_platform_from_path('test')
    out, err = capfd.readouterr()
    # Assert something is printed (a warning)
    assert out
