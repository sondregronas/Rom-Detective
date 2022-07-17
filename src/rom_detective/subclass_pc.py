from dataclasses import dataclass

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform, PlatformFlag
from rom_detective._globals_ import PLATFORMS, DATABASES


"""
Windows Games
"""


@dataclass
class SteamLibraryIndexItem(IndexerItem):
    """
    source input: dict(steam_folder: game_id)
    source output: URL to steam://rungameid/<id>
    platform.flag = PlatformFlag.STEAM
    """
    source: any = None
    platform: Platform = PLATFORMS['win']

    g_id: str = ''

    def __str__(self) -> str:
        """String representation"""
        return f'{self.title} ({self.platform.name} [steamid:{self.g_id}])'

    def subclass_init(self) -> None:
        """Get steam game name from the .acf file and set source to the rungameid url"""
        self.g_id: str = list(self.source.values())[0]
        self.platform.flag = PlatformFlag.STEAM
        self.filename = self.get_steam_name()
        self.source = f'URL=steam://rungameid/{self.g_id}'
        self.clean_brackets = False

    def get_steam_name(self) -> str:
        """Read the game id's appmanifest and extract name key value"""
        name = open(f'{list(self.source.keys())[0]}\\steamapps\\appmanifest_{self.g_id}.acf', 'rb').read().decode('UTF-8')
        name = name.split('\t"name"\t\t"')[1].split('"')[0]
        return f'{name}.url'

    @property
    def blacklisted(self) -> bool:
        return True if self.g_id in DATABASES.blacklist_steam_software.keys() else False
