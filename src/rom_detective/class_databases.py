__all__ = ['DatabaseFiles']

from dataclasses import dataclass

from rom_detective._const_ import DATA_FOLDER


def load_db(path: str) -> dict:
    """Takes a database filepath (key=value format) and returns a dict ({key:value})"""
    return {entry.split('=')[0]: entry.split('=')[1]
            for entry in open(path, "r", encoding='utf8')
            if not entry.startswith('#')}


@dataclass
class DatabaseFiles:
    """
    DatabaseFiles
        .gameslist_ps3 = dict(game_id:full_title)
        .blacklist_steam_software = dict(steam_id:full_title)
    """
    gameslist_ps3 = load_db(f'{DATA_FOLDER}\\gameslist_ps3.txt')
    blacklist_steam_software = load_db(f'{DATA_FOLDER}\\blacklist_steam_software.txt')
