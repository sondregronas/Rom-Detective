from tests import *

from rom_detective.rom_detective import RomDetective, RDFlag


def test_ps3():
    rd = RomDetective()

    rd.add_rom_folder(f'{TEST_ROMS_PATH}\\playstation 3')
    rd.index_all()

    assert rd.games
    assert 'Test ROM.BIN' in [game.filename for game in rd.games]
    assert rd.games[0].source.endswith('PS3_GAME\\USRDIR\\EBOOT.BIN')
    assert len(rd.games) == 3
    assert len(rd.stats[RDFlag.INDEXED]) == 2
    assert len(rd.stats[RDFlag.BLACKLISTED]) == 1


def test_steam():
    rd = RomDetective()

    rd.add_steam_folder(f'{TEST_FILES_PATH}\\steam')
    rd.index_all()

    assert rd.games
    assert 'Steamworks Common Redistributables.url' in [game.filename for game in rd.games]
    assert 'test2.url' in [game.filename for game in rd.games]
    assert len(rd.stats[RDFlag.INDEXED]) == 2
    assert len(rd.stats[RDFlag.BLACKLISTED]) == 1


def test_all():
    rd = RomDetective()

    rd.add_rom_folder(TEST_ROMS_PATH)
    rd.add_steam_folder(f'{TEST_FILES_PATH}\\steam')
    rd.index_all()

    assert len(rd.games) == 19
    assert len(rd.stats[RDFlag.INDEXED]) == 13
    assert len(rd.stats[RDFlag.BLACKLISTED]) == 6
