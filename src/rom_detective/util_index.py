import os
import glob
import vdf

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform
from rom_detective.subclass_consoles import PS3IndexItem, WiiUIndexItem
from rom_detective.subclass_pc import SteamLibraryIndexItem
from rom_detective._globals_ import PLATFORMS


def list_all_of_type(directory: str, extensions: list, recursive: bool = True) -> list[str]:
    """
    Takes a directory path to scan files from
    Returns abspath to ALL files matching any extension from a list of extensions
    """
    path = f'{directory}\\**/*.*' if recursive else f'{directory}\\*.*'
    return [file for file in glob.glob(path, recursive=recursive)
            if os.path.splitext(file)[1] in extensions]


def list_subfolders(directory: str, children: int = 2) -> list[str]:
    """
    Takes a root directory path and iterates through <int> amount
    of children and returns a list of abs-paths
    """
    output = list()
    layer = list([directory])
    for i in range(children):
        result = list()
        for directory in layer:
            result += [f'{directory}\\{subdir}' for subdir in next(os.walk(directory))[1]]
        output += result
        layer = result.copy()
    return output


def index_generic_rom_folder(path: str, platform: Platform) -> list[IndexerItem]:
    return [IndexerItem(source=file, platform=platform)
            for file in list_all_of_type(path, platform.extensions)]


def index_ps3_folder(path: str, children: int = 2) -> list[PS3IndexItem]:
    """
    Takes a path to a folder containing PS3 ROM directories (including 2 children)
    returns a list of PS3Rom objects

    PS3 game ids are always 9ch in length
    """
    return [PS3IndexItem(f"{directory}\\{os.path.basename(directory)}")
            for directory in list_subfolders(path, children=children)
            if len(os.path.basename(directory)) == 9]


def index_switch_folder(path: str) -> list[IndexerItem]:
    """
    Take a path to a folder containing switch games for any valid ROM
    scans EVERY children in directory

    Blacklists items if they're indexed as DLC or Updates

    returns a list of IndexerItems
    """
    roms = [IndexerItem(source=rom, platform=PLATFORMS['switch'])
            for rom in list_all_of_type(path, PLATFORMS['switch'].extensions)]
    # TODO: Find a better way to handle dlc/update checks
    [rom.blacklist() for rom in roms if 'dlc' in rom.source.lower() or 'update' in rom.source.lower()]
    return roms


def index_wiiu_folder(path: str) -> list[WiiUIndexItem]:
    """
    Takes a Wii U ROM directory and returns a list of
    all matching .wux and code/*.rpx entries

    Entries in 'update' or 'dlc' folders are blacklisted by the subclass
    """
    output = list()
    relevant_folders = [path] + [folder for folder in list_subfolders(path, children=3)
                                 if 'content' not in folder.split(path)[1].split('\\')
                                 and 'meta' not in folder.split(path)[1].split('\\')]

    for folder in relevant_folders:
        output += [WiiUIndexItem(source=file, platform=PLATFORMS['wiiu'])
                   for file in list_all_of_type(folder, PLATFORMS['wiiu'].extensions, recursive=False)]
    return output


def index_steam_library(primary_steam_dir: str) -> list[SteamLibraryIndexItem]:
    """
    Takes the primary steam directory (C:\\Program Files (x86)\\Steam)
    Reads steamapps\\libraryfolders.vdf for installed titles

    Returns a list of SteamItems, which fetches metadata from their respected paths

    TODO: Simplify?
    """
    output = list()
    try:
        steam_vdf = vdf.load(open(f'{primary_steam_dir}\\steamapps\\libraryfolders.vdf'))
    except FileNotFoundError:  # pragma: no cover
        print(f'The provided Steam directory is invalid ({primary_steam_dir})')
        return output

    # Create a dict for every {path: list[game_id]}
    path_id_pairs = {steam_vdf['libraryfolders'][entries]['path']: steam_vdf['libraryfolders'][entries]['apps']
                     for entries in steam_vdf['libraryfolders']}

    for path, game_ids in path_id_pairs.items():
        output += [SteamLibraryIndexItem({path: game_id}) for game_id in game_ids]

    return output


def index_rom_folder_from_platform(path: str, platform: Platform) -> list[IndexerItem]:
    """Check if platform id is in methods, if not do 'default'"""
    methods = {
        'ps3': index_ps3_folder,
        'wiiu': index_wiiu_folder,
        'switch': index_switch_folder,
        'default': index_generic_rom_folder
    }
    return methods[platform.id](path) if platform.id in methods.keys() else methods['default'](path, platform)
