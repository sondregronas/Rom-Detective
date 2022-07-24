import os
import re
import vdf

from pathlib import Path
from xml.dom import minidom
from dataclasses import dataclass, field

from rom_detective import CONF_FOLDER, ILLEGAL_CHARACTERS
from rom_detective.platforms import Platform, PlatformFlag
from rom_detective.util import scan_for_files, list_subfolders
import rom_detective.const as const


@dataclass
class Item:
    source: str
    platform: Platform
    filename: str = None
    clean_brackets: bool = True
    whitelisted: bool = False
    _blacklist: bool = field(init=False, repr=False, default=False)

    def __post_init__(self) -> None:
        """Set filename from path unless specified, then sanitize the filename"""
        self.subclass_init()
        self.blacklist(force=False)
        self.whitelist(force=False)
        self.filename = self.source.split('\\')[-1] if not self.filename else self.filename
        self.sanitize_filename()

    def subclass_init(self) -> None:
        """For subclasses"""
        pass

    def __str__(self) -> str:
        """String representation"""
        return f'{self.title} ({self.platform})'

    @property
    def title(self) -> str:
        """Returns the filename without file extension"""
        return os.path.splitext(self.filename)[0]

    @property
    def extension(self) -> str:
        """Returns the extension (including dot). Returns an empty string if none found"""
        return os.path.splitext(self.filename)[1]

    @property
    def blacklisted(self) -> bool:
        """Used by some ROM/Game types"""
        return False or self._blacklist

    def blacklist(self, force: bool = True) -> None:
        """Override for <blacklisted> (Manually defined)"""
        if force:
            self._blacklist = force
            return
        try:
            self._blacklist = self.source in open(f'{CONF_FOLDER}\\blacklist.cfg',
                                                  "r", encoding='utf8').read().split('\n')
        except FileNotFoundError as e:  # pragma: no cover
            print(f'Warning: {e}')
            self._blacklist = False

    def whitelist(self, force: bool = True) -> None:
        """Override for <blacklisted> (Manually defined)"""
        if force:
            self.whitelisted = force
            return
        try:
            self.whitelisted = self.source in open(f'{CONF_FOLDER}\\whitelist.cfg',
                                                   "r", encoding='utf8').read().split('\n')
        except FileNotFoundError as e:  # pragma: no cover
            print(f'Warning: {e}')
            self.whitelisted = False

    def sanitize_filename(self) -> str:
        """
        Used by ROM/Game classes to reformat the filename

        - 1. Moves occurrences of ', The' to the front
        - 2. Removes illegal characters
        - 3. (clean_brackets flag) Removes parentheses and blocks,
                                   excluding those containing digits (Disc 1)
                                   Useful for most platforms, but not all
        - 4. Fix some unicode characters
        - 5. Remove excess whitespace
        """
        name, ext = os.path.splitext(self.filename)

        # 1. ', The' to 'The *'
        if ', the' in name.lower():
            name = re.sub(r', the', '', name, flags=re.IGNORECASE)
            name = f'The {name}'

        # 2. Omit illegal characters
        name = re.sub(f'[{ILLEGAL_CHARACTERS}]', '', name)

        # 3. (Optional) Remove (*) and [*] (excl. (*0-9))
        # TODO: Find a better solution to handle parentheses?
        name = re.sub(r'\([^\d\)]*\)|\[[^\]]*\]', '', name) if self.clean_brackets else name
        ###

        # 4. Unicode fixes
        name = name.replace('&amp;', '&')

        # 5. Excess Whitespace
        name = re.sub('[_ ]+', ' ', name).strip()

        name = f'{name}{ext}'
        self.filename = name
        return self.filename


"""
Subclasses
"""


@dataclass
class PS3Item(Item):
    """
    Takes a source (path) to the 9ch ROM folder
    and retrieves name from data/gameslist_ps3.txt
    """
    platform: Platform = const.PLATFORMS['ps3']

    g_id: str = ''

    def subclass_init(self) -> None:
        """Append EBOOT.BIN path and get filename from data/gameslist_ps3.txt"""
        self.g_id = self.source.split('\\')[-1]
        self.source += r'\PS3_GAME\USRDIR\EBOOT.BIN'
        try:
            self.filename = const.DATABASES.gameslist_ps3[self.g_id] if not self.filename else self.filename
        except KeyError:
            print(f'Warning (PS3): {self.g_id} is not a valid PS3 ID and will be blacklisted')
        self.clean_brackets = False

    @property
    def blacklisted(self) -> bool:
        return self.g_id not in const.DATABASES.gameslist_ps3.keys()


@dataclass
class WiiUItem(Item):
    """
    Takes a source (path) to a ROM file, see platforms.yaml,
    if ROM file is .rpx, retrieve the filename from metadata
    """
    platform: Platform = const.PLATFORMS['wiiu']

    def subclass_init(self) -> None:
        """Find filename from meta.xml, if applicable"""
        if self.source.lower().endswith('.rpx') and not self.filename:
            self.filename = self._find_name_from_meta()

    def _find_name_from_meta(self) -> str:
        """Finds longname_en from 'meta.xml', derived from a .rpx source path"""
        try:
            path = f'{Path(self.source).parents[1]}\\meta\\meta.xml'
            meta = minidom.parse(path).getElementsByTagName('longname_en')
            new_name = meta[0].firstChild.nodeValue.replace('\n', ' ').strip()
        except FileNotFoundError:
            path = os.path.basename(Path(self.source).parents[1])
            print(f'meta.xml not found for {self.source}, using folder name instead ({path})')
            new_name = path
        return f'{new_name}.rpx'

    @property
    def blacklisted(self) -> bool:
        """If path contains dlc or update, blacklist it"""
        # TODO: Find a better implementation(?)
        dlc_or_update = 'dlc' in self.source.lower() or 'update' in self.source.lower()
        return dlc_or_update if self.source.lower().endswith('.rpx') else False


@dataclass
class SteamItem(Item):
    """
    source input: dict(steam_folder: game_id)
    source output: URL to steam://rungameid/<id>
    platform.flag = PlatformFlag.STEAM
    """
    platform: Platform = const.PLATFORMS['win']
    g_id: str = ''

    def __str__(self) -> str:
        """String representation"""
        return f'{self.title} ({self.platform.name} [steamid:{self.g_id}])'

    def subclass_init(self) -> None:
        """Get steam game name from the .acf file and set source to the rungameid url"""
        self.platform.flag = PlatformFlag.STEAM
        self.filename = self.get_steam_name()
        self.source = f'URL=steam://rungameid/{self.g_id}'
        self.clean_brackets = False

    def get_steam_name(self) -> str:
        """Read the game id's appmanifest and extract name key value"""
        name = open(f'{self.source}\\steamapps\\appmanifest_{self.g_id}.acf', 'rb').read().decode('UTF-8')
        name = name.split('\t"name"\t\t"')[1].split('"')[0]
        return f'{name}.url'

    @property
    def blacklisted(self) -> bool:
        return True if self.g_id in const.DATABASES.blacklist_steam_software.keys() else False


"""
Functions
"""


def index_generic_folder(path: str, platform: Platform) -> list[Item]:
    return [Item(source=file, platform=platform)
            for file in scan_for_files(path, extensions=platform.extensions)]


def index_ps3_folder(path: str, children: int = 2) -> list[PS3Item]:
    """
    Takes a path to a folder containing PS3 ROM directories (including 2 children)
    returns a list of PS3Rom objects

    PS3 game ids are always 9ch in length
    """
    return [PS3Item(f"{directory}\\{os.path.basename(directory)}")
            for directory in list_subfolders(path, children=children)
            if len(os.path.basename(directory)) == 9]


def index_switch_folder(path: str) -> list[Item]:
    """
    Take a path to a folder containing switch games for any valid ROM
    scans EVERY children in directory

    Blacklists items if they're indexed as DLC or Updates

    returns a list of IndexerItems
    """
    roms = [Item(source=rom, platform=const.PLATFORMS['switch'])
            for rom in scan_for_files(path, extensions=const.PLATFORMS['switch'].extensions)]
    # TODO: Find a better way to handle dlc/update checks
    [rom.blacklist() for rom in roms if 'dlc' in rom.source.lower() or 'update' in rom.source.lower()]
    return roms


def index_wiiu_folder(path: str) -> list[WiiUItem]:
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
        output += [WiiUItem(source=file, platform=const.PLATFORMS['wiiu'])
                   for file in scan_for_files(folder, extensions=const.PLATFORMS['wiiu'].extensions, recursive=False)]
    return output


def index_steam_library(primary_steam_dir: str) -> list[SteamItem]:
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

    for lib_folder, g_ids in path_id_pairs.items():
        output += [SteamItem(source=lib_folder, g_id=g_id) for g_id in g_ids]

    return output


def _index_pair(path: str, platform: Platform) -> list[Item]:
    """Check if platform id is in methods, if not do 'default'"""
    methods = {
        'ps3': index_ps3_folder,
        'wiiu': index_wiiu_folder,
        'switch': index_switch_folder,
        'default': index_generic_folder
    }
    return methods[platform.id](path) if platform.id in methods.keys() else methods['default'](path, platform)


def index_pairs(pairs: dict) -> list[Item]:
    """Takes a dict of {path: platform}, returns a list of Items (ROMs)"""
    # filtered_pairs = {k: v for k, v in pairs.items() if v}
    return [_index_pair(path, platform) for path, platform in pairs.items() if platform][0]
