from rom_detective.class_indexer_item import IndexerItem

from rom_detective.subclass_consoles import WiiUIndexItem

from rom_detective.util_index import (
    index_ps3_folder,
    index_switch_folder,
    index_wiiu_folder,
    index_steam_library,
    index_rom_folder_from_platform,
)

from test_const import TEST_ROMS_PATH, TEST_FILES_PATH

from rom_detective._globals_ import PLATFORMS


def test_index_ps3():
    roms = index_ps3_folder(f'{TEST_ROMS_PATH}\\playstation 3')
    assert roms[0].platform.id == 'ps3'


def test_index_switch():
    roms = index_switch_folder(f'{TEST_ROMS_PATH}\\switch')
    rom = IndexerItem(source=f'{TEST_ROMS_PATH}\\switch\\test.nsp', platform=PLATFORMS['switch'])
    assert rom in roms

    # Ensure 5 ROMs were found
    assert len(roms) == 5
    # Ensure 2/5 were blacklisted (DLC / Update)
    assert len([rom for rom in roms if rom.blacklisted]) == 2


def test_index_wiiu():
    roms = index_wiiu_folder(f'{TEST_ROMS_PATH}\\wiiu')

    rom = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test.wux', platform=PLATFORMS['wiiu'])
    assert rom in roms

    rom = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test\\code\\test.rpx', platform=PLATFORMS['wiiu'])
    assert rom in roms

    # Ensure 5 ROMs were found. Only .rpx in 'code' folders or '.wux. folders
    assert len(roms) == 5
    # Ensure 2/5 were blacklisted (DLC / Update)
    assert len([rom for rom in roms if rom.blacklisted]) == 2


def test_index_steam_library():
    games = index_steam_library(f'{TEST_FILES_PATH}\\steam')
    assert len(games) == 3


def test_index_generic_from_platform():
    roms = index_rom_folder_from_platform(f'{TEST_ROMS_PATH}\\wiiu', PLATFORMS['wiiu'])
    assert len(roms) == 5

    roms = index_rom_folder_from_platform(f'{TEST_ROMS_PATH}\\n64', PLATFORMS['n64'])
    assert len(roms) == 3
