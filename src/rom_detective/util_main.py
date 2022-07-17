from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform, identify_platform, PlatformFlag
from rom_detective.util_index import list_subfolders, index_rom_folder_from_platform
from rom_detective._globals_ import PLATFORMS


def identify_platform_from_path(path: str) -> Platform:
    """
    Returns a single platform if a folder name in the given path
    matches any of the alias entries in 'data/platforms.yaml'
    """
    try:
        return identify_platform(path, PLATFORMS.values())
    except Warning as e:
        print(e)


def identify_platforms_from_path(path: str) -> dict[Platform]:
    """
    Returns a dict of platforms for every directory in the given path that
    matches any of the alias entries in 'data/platforms.yaml'

    Format: {path: Platform}
    """
    return {directory: identify_platform_from_path(directory)
            for directory in list_subfolders(path, children=1)
            if identify_platform_from_path(directory)}


def index_roms_from_dict(pairs: dict) -> list[IndexerItem]:
    """
    Takes a dict of {path: platform}, removes empty/NoneType key/values
    Calls index_folder_from_platform with the remaining keys/values

    returns a list of IndexerItems (ROMs)
    """
    filtered_pairs = {k: v for k, v in pairs.items() if v and v.flag == PlatformFlag.DEF_ROM}
    roms = list()
    for path in filtered_pairs:
        roms += index_rom_folder_from_platform(path, filtered_pairs[path])
    return roms
