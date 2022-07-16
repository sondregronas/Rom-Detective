import os

from pathlib import Path
from xml.dom import minidom
from dataclasses import dataclass

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform
from rom_detective._globals_ import PLATFORMS, DATABASES


"""
Console ROMs
    - PS3IndexItem - takes path to 9ch ROM folder & looks up data in database
    - WiiUIndexItem - takes path to Wii U ROMs, if .RPX, find metadata
"""


@dataclass
class PS3IndexItem(IndexerItem):
    """
    Takes a source (path) to the 9ch ROM folder
    and retrieves name from data/gameslist_ps3.txt
    """
    platform: Platform = PLATFORMS['ps3']

    def subclass_init(self) -> None:
        """Append EBOOT.BIN path and get filename from data/gameslist_ps3.txt"""
        self.g_id = self.source.split('\\')[-1]
        self.source += r'\PS3_GAME\USRDIR\EBOOT.BIN'
        try:
            self.filename = DATABASES.gameslist_ps3[self.g_id] if not self.filename else self.filename
        except KeyError:
            print(f'Warning (PS3): {self.g_id} is not a valid PS3 ID and will be blacklisted')
        self.clean_brackets = False

    @property
    def blacklisted(self) -> bool:
        return self.g_id not in DATABASES.gameslist_ps3.keys()


@dataclass
class WiiUIndexItem(IndexerItem):
    """
    Takes a source (path) to a ROM file, see platforms.yaml,
    if ROM file is .rpx, retrieve the filename from metadata
    """
    platform: Platform = PLATFORMS['wiiu']

    def subclass_init(self) -> None:
        """Find filename from meta.xml, if applicable"""
        if self.source.lower().endswith('.rpx') and not self.filename:
            self.filename = self.find_name_from_meta()

    def find_name_from_meta(self) -> str:
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
