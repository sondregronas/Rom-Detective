import pytest

from rom_detective._globals_ import PLATFORMS
from rom_detective.class_gui import RomDetectiveGui, GuiItemFlag
from rom_detective.class_indexer_item import IndexerItem

from test_const import TEST_FILES_PATH, TEST_ROMS_PATH


def test_gui_rom_folders():
    test_gui = RomDetectiveGui()

    # Ensure test_gui has zero platforms
    assert not test_gui.platforms.values()

    # Add ALL roms from ROM folder
    test_gui.add_rom_folder(TEST_ROMS_PATH)
    assert PLATFORMS['wiiu'] in test_gui.platforms.values()

    # Remove Wii U folder from gui
    before_removal = len(test_gui.platforms)

    test_gui.remove_folder(f'{TEST_ROMS_PATH}\\wiiu')
    assert PLATFORMS['wiiu'] not in test_gui.platforms.values()
    assert before_removal > len(test_gui.platforms)

    # Re-add Wii U folder
    test_gui.add_rom_folder(f'{TEST_ROMS_PATH}\\wiiu')
    assert PLATFORMS['wiiu'] in test_gui.platforms.values()
    assert before_removal == len(test_gui.platforms)


def test_gui_steam_folder():
    test_gui = RomDetectiveGui()

    # Add Steam Folder and ensure a windows platform is added
    assert PLATFORMS['win'] not in test_gui.platforms.values()
    assert f'{TEST_FILES_PATH}\\steam' not in test_gui.platforms.keys()

    test_gui.add_steam_folder(f'{TEST_FILES_PATH}\\steam')

    assert f'{TEST_FILES_PATH}\\steam' in test_gui.platforms.keys()

    # Overwrite steam folder
    test_gui.add_steam_folder(f'{TEST_FILES_PATH}\\steam2')
    assert f'{TEST_FILES_PATH}\\steam' not in test_gui.platforms.keys()
    assert f'{TEST_FILES_PATH}\\steam2' in test_gui.platforms.keys()

    # Remove steam folder
    test_gui.remove_steam_folder()
    assert f'{TEST_FILES_PATH}\\steam' not in test_gui.platforms.keys()
    assert f'{TEST_FILES_PATH}\\steam2' not in test_gui.platforms.keys()
    assert PLATFORMS['win'] not in test_gui.platforms.values()


def test_gui_index():
    test_gui = RomDetectiveGui()

    test_gui.add_rom_folder(TEST_ROMS_PATH)
    test_gui.add_steam_folder(f'{TEST_FILES_PATH}\\steam')

    assert len(test_gui.stats) == 0
    test_gui.index_all()

    # 19 games should added in total
    assert len(test_gui.games) == 19
    assert len(test_gui.stats[GuiItemFlag.INDEXED]) == 13
    assert len(test_gui.stats[GuiItemFlag.BLACKLISTED]) == 6
    assert len(test_gui.stats[GuiItemFlag.WHITELISTED]) == 0

    # Ensure games return IndexerItems
    for game in test_gui.games:
        assert issubclass(type(game), IndexerItem)

    # 1 blacklisted steam game, 2 indexed
    assert len(test_gui.stats_by_platform(PLATFORMS['win'])[GuiItemFlag.BLACKLISTED]) == 1
    assert len(test_gui.stats_by_platform(PLATFORMS['win'])[GuiItemFlag.WHITELISTED]) == 0
    assert len(test_gui.stats_by_platform(PLATFORMS['win'])[GuiItemFlag.INDEXED]) == 2

    # 3 indexed n64 games
    assert len(test_gui.stats_by_platform(PLATFORMS['n64'])[GuiItemFlag.INDEXED]) == 3


def test_force_platform():
    test_gui = RomDetectiveGui()

    test_gui.add_rom_folder(TEST_ROMS_PATH)
    assert PLATFORMS['n64'] in test_gui.platforms.values()
    assert test_gui.platforms[f'{TEST_ROMS_PATH}\\n64'] == PLATFORMS['n64']

    # Scan with n64 folder as n64
    test_gui.index_all()
    assert len(test_gui.games) == 16

    test_gui.specify_platform(f'{TEST_ROMS_PATH}\\n64', PLATFORMS['wiiu'])
    assert PLATFORMS['n64'] not in test_gui.platforms.values()
    assert test_gui.platforms[f'{TEST_ROMS_PATH}\\n64'] == PLATFORMS['wiiu']

    # N64 games should get removed (folders re-index), when platform re-specified
    assert len(test_gui.games) < 16


def test_modify_indexed_folders():
    test_gui = RomDetectiveGui()

    test_gui.add_rom_folder(TEST_ROMS_PATH)
    test_gui.add_steam_folder(f'{TEST_FILES_PATH}\\steam')
    test_gui.index_all()
    assert len(test_gui.games) == 19
    assert len(test_gui.platforms) == 5

    test_gui.remove_steam_folder()
    assert len(test_gui.games) < 19
    assert len(test_gui.platforms) == 4

    # Ensure ROM folders can be classified as win_platforms, and vice versa
    assert PLATFORMS['win'] != test_gui.platforms[f'{TEST_ROMS_PATH}\\n64']
    test_gui.specify_platform(f'{TEST_ROMS_PATH}\\n64', PLATFORMS['win'])
    assert PLATFORMS['win'] == test_gui.platforms[f'{TEST_ROMS_PATH}\\n64']

    assert f'{TEST_FILES_PATH}\\steam' not in test_gui.platforms.keys()
    test_gui.specify_platform(f'{TEST_FILES_PATH}\\steam', PLATFORMS['n64'])
    assert f'{TEST_FILES_PATH}\\steam' in test_gui.platforms.keys()
    assert PLATFORMS['n64'] == test_gui.platforms[f'{TEST_FILES_PATH}\\steam']


def test_index_platform_from_path():
    test_gui = RomDetectiveGui()
    test_gui.add_rom_folder(TEST_ROMS_PATH)

    assert len(test_gui.games) == 0
    test_gui.index_platform_from_path(f'{TEST_ROMS_PATH}\\n64')
    assert len(test_gui.games) >= 1