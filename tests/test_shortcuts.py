import pytest

from rom_detective._const_ import DEFAULT_TARGET_FOLDER
from rom_detective._globals_ import PLATFORMS

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.util_shortcuts import create_shortcut, get_destination_folder
from rom_detective.subclass_consoles import PS3IndexItem
from rom_detective.subclass_pc import SteamLibraryIndexItem
from test_const import TEST_FILES_PATH, TEST_ROMS_PATH


@pytest.mark.createfiles(reason='Creates folders & files, use --create-files flag to run')
def test_get_destination_folder():
    test = get_destination_folder('Test Name.file', PLATFORMS["win"])
    assert test == f'{DEFAULT_TARGET_FOLDER}\\{PLATFORMS["win"].name}\\Test Name.file'


@pytest.mark.createfiles(reason='Creates folders & files, use --create-files flag to run')
def test_create_shortcut():
    # .url
    test_rom = SteamLibraryIndexItem({f'{TEST_FILES_PATH}\\steam': '0123456789'})
    test = create_shortcut(test_rom)
    assert f'{DEFAULT_TARGET_FOLDER}\\{test_rom.platform.name}\\{test_rom.filename}->{test_rom.source}' in test['success']

    # .lnk (File is unimportant, platform=win is)
    test_rom = IndexerItem(f'{TEST_FILES_PATH}\\n64\\test.z64', platform=PLATFORMS['win'], filename='test.lnk')
    test = create_shortcut(test_rom)
    assert f'{DEFAULT_TARGET_FOLDER}\\{test_rom.platform.name}\\{test_rom.filename}->{test_rom.source}' in test['success']

    # Ensure sure .lnk is automatically appended, if not specified (and is not .url)
    test_rom = IndexerItem(f'{TEST_FILES_PATH}\\n64\\test.z64', platform=PLATFORMS['win'], filename='test2.exe')
    test = create_shortcut(test_rom)
    assert f'{DEFAULT_TARGET_FOLDER}\\{test_rom.platform.name}\\{test_rom.filename}.lnk->{test_rom.source}' in test['success']
    
    # .symlink
    test_rom = PS3IndexItem(f'{TEST_ROMS_PATH}\\playstation 3\\exampleid')
    test = create_shortcut(test_rom)
    assert f'{DEFAULT_TARGET_FOLDER}\\{test_rom.platform.name}\\{test_rom.filename}->{test_rom.source}' in test['success']


@pytest.mark.createfiles(reason='Creates folders & files, use --create-files flag to run')
def test_duplicate_symlink(capfd):
    test_rom = PS3IndexItem(f'{TEST_ROMS_PATH}\\playstation 3\\exampleid')
    create_shortcut(test_rom)
    create_shortcut(test_rom)
    out, err = capfd.readouterr()
    assert 'Shortcut already exists' in out


def test_dry_run():
    test_rom = SteamLibraryIndexItem({f'{TEST_FILES_PATH}\\steam': '0123456789'})
    test = create_shortcut(test_rom, dry_run=True)
    assert f'{DEFAULT_TARGET_FOLDER}\\{test_rom.platform.name}\\{test_rom.filename}->{test_rom.source}' in test['dry_run']


def test_dry_blacklist():
    test_rom = SteamLibraryIndexItem({f'{TEST_FILES_PATH}\\steam': '228980'})
    test = create_shortcut(test_rom, dry_run=True)
    assert 'blacklist' in test.keys()


def test_dry_whitelist():
    test_rom = SteamLibraryIndexItem({f'{TEST_FILES_PATH}\\steam': '228980'})
    test_rom.whitelisted = True
    test = create_shortcut(test_rom, dry_run=True)
    assert f'{DEFAULT_TARGET_FOLDER}\\{test_rom.platform.name}\\{test_rom.filename}->{test_rom.source}' in test['dry_run']
