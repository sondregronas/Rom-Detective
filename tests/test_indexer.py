from rom_detective.class_indexer_item import IndexerItem
from rom_detective.subclass_consoles import PS3IndexItem, WiiUIndexItem
from rom_detective.subclass_pc import SteamLibraryIndexItem
from rom_detective._const_ import ILLEGAL_CHARACTERS

from test_const import TEST_FILES_PATH, TEST_ROMS_PATH


def test_console_filename():
    """Test sanitization of strings"""
    # Undefined filenames
    test = IndexerItem(source=f'{ILLEGAL_CHARACTERS}test', platform=None)
    assert test.source == f'{ILLEGAL_CHARACTERS}test'
    assert test.filename == 'test'
    assert test.title == 'test'
    assert test.extension == ''

    test = IndexerItem(source=' _t___e     s _ _ __ t   __.url', platform=None)
    assert test.source == ' _t___e     s _ _ __ t   __.url'
    assert test.filename == 't e s t.url'
    assert test.title == 't e s t'
    assert test.extension == '.url'

    # Defined filenames
    test = IndexerItem(source=f'abc', filename='t  _e __ s___t   __.url', platform=None)
    assert test.source == f'abc'
    assert test.filename == 't e s t.url'

    test = IndexerItem(source=f'{ILLEGAL_CHARACTERS}test', filename=f'{ILLEGAL_CHARACTERS}test2', platform=None)
    assert test.source == f'{ILLEGAL_CHARACTERS}test'
    assert test.filename == 'test2'

    # Clean_brackets
    test = IndexerItem(source=f'test (test) (With digits 123)', platform=None, clean_brackets=True)
    assert test.filename == 'test (With digits 123)'

    test = IndexerItem(source=f'test (test) [test]', platform=None, clean_brackets=True)
    assert test.filename == 'test'

    test = IndexerItem(source=f'test (test) [test]', platform=None, clean_brackets=False)
    assert test.filename == 'test (test) [test]'

    # *, The* to The*
    test = IndexerItem(source=f'Test, the', platform=None)
    assert test.filename == 'The Test'


def test_console_blacklist():
    test = IndexerItem(source=f'test', platform=None)
    assert not test.blacklisted


def test_console_str():
    test = IndexerItem(source=f'test', platform=None, clean_brackets=False)
    assert str(test) == 'test (None)'


#####################
# SUBCLASS_CONSOLES #
#####################


def test_ps3_item():
    # Ensure valid ID works
    test = PS3IndexItem(source=f'{TEST_ROMS_PATH}\\playstation 3\\exampleid')
    assert test.source == f'{TEST_ROMS_PATH}\\playstation 3\\exampleid\\PS3_GAME\\USRDIR\\EBOOT.BIN'
    assert test.filename == 'Test ROM'
    assert test.platform.id == 'ps3'
    assert not test.blacklisted

    # Ensure invalid IDs get blacklisted
    test = PS3IndexItem(source=f'{TEST_ROMS_PATH}\\playstation 3\\invalidid')
    assert test.blacklisted


def test_wiiu_item():
    # Ensure .wux works
    test = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test.wux')
    assert test.platform.id == 'wiiu'
    assert test.filename == 'test.wux'
    assert not test.blacklisted

    # Ensure .rpx works, with meta.xml
    test = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test\\code\\test.rpx')
    assert test.filename == 'Test Wii U Game.rpx'
    assert not test.blacklisted

    # Ensure .rpx works, without meta.xml
    test = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test2\\code\\test.rpx')
    assert test.filename == 'test2.rpx'
    assert not test.blacklisted

    # Ensure updates and dlc are blacklisted
    # TODO: Make a better distinction between update/dlc
    test = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test2\\update\\test.rpx')
    assert test.blacklisted
    test = WiiUIndexItem(source=f'{TEST_ROMS_PATH}\\wiiu\\test2\\dlc\\test.rpx')
    assert test.blacklisted


###############
# SUBCLASS_PC #
###############


def test_steam_item():
    test = SteamLibraryIndexItem({f'{TEST_FILES_PATH}\\steam': '228980'})
    assert str(test) == 'Steamworks Common Redistributables (Windows [steamid:228980])'
    assert test.filename.endswith('.url')
    assert test.source == 'URL=steam://rungameid/228980'
    assert test.platform.id == 'win'
    assert test.blacklisted

    test = SteamLibraryIndexItem({f'{TEST_FILES_PATH}\\steam': '0123456789'})
    assert test.filename.endswith('.url')
    assert not test.blacklisted
