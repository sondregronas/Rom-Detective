from dataclasses import dataclass, field

from rom_detective._globals_ import PLATFORMS

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform, PlatformFlag

from rom_detective.util_main import (
    identify_platform_from_path,
    identify_platforms_from_path,
    index_roms_from_dict,
)
from rom_detective.util_index import (
    index_steam_library,
)


@dataclass
class GuiItemFlag:
    INDEXED = 'indexed'
    WHITELISTED = 'whitelisted'
    BLACKLISTED = 'blacklisted'


"""
RomDetectiveGui
===============
Work in progress
"""


@dataclass
class RomDetectiveGui:
    platforms: dict[str, Platform] = field(default_factory=dict)
    games: list[IndexerItem] = field(default_factory=list)
    stats: dict[str, list] = field(default_factory=dict)
    _steam_folder: str = field(default_factory=str)

    def add_folder_roms(self, path: str) -> None:
        """
        Add a new folder and try to identify the platform,
        if none specified, attempt to identify its subdirectories (1 layer)

        If none found - allow user to specify manually. User should also be able to override the platform
        """
        platform = identify_platform_from_path(path)
        self.platforms.update({path: platform} if platform else
                              identify_platforms_from_path(path))
        # TODO: If platform not identified, add just the path and allow user to specify platform

    def _platform_changes_made(self) -> None:
        """Called when changes are made"""
        # TODO: Delete associated items from self.games, without forced re-index of everything
        if self.stats:
            self.index_all()
            self.update_stats()

    def remove_folder(self, path: str) -> None:
        """
        Remove a folder (requires just the path),
        remove any associated platforms/indexed items
        """
        self.platforms.pop(path, None)

        self._platform_changes_made()

    def specify_platform(self, path: str, platform: Platform) -> None:
        """Overwrite the platform value for a given path"""
        self.platforms.pop(path, None)
        self.platforms[path] = platform

        self._platform_changes_made()

    def index_platform_from_path(self, path: str, update_stats=True) -> list[IndexerItem]:
        """Index ROMs/Games from a specific platform"""
        if self.platforms[path].flag == PlatformFlag.DEF_ROM:
            self.games += index_roms_from_dict({path: self.platforms[path]})
        elif self.platforms[path].flag == PlatformFlag.STEAM:
            self.games += index_steam_library(self.steam_folder)
        else:  # pragma: no cover
            raise RuntimeError(f'Couldn\'t index items ({path}: {self.platforms[path]}')

        # Optional flag to not force an update (used by index_all)
        if update_stats:
            self.update_stats()

        return self.games

    def index_all(self) -> None:
        """Index everything and append to self.games, then update stats"""
        del self.games
        self.games = list()

        [self.index_platform_from_path(path, update_stats=False) for path in self.platforms.keys()]

        self.update_stats()

    def update_stats(self) -> dict:
        """Deletes self.stats, then rebuilds it"""
        del self.stats
        self.stats = dict()

        self.stats[GuiItemFlag.WHITELISTED] = [game for game in self.games if game.whitelisted]
        self.stats[GuiItemFlag.BLACKLISTED] = [game for game in self.games if game.blacklisted and not game.whitelisted]
        self.stats[GuiItemFlag.INDEXED] = [game for game in self.games if not game.blacklisted or game.whitelisted]

        return self.stats

    def stats_by_platform(self, platform: Platform) -> dict:
        """Get the stats for a given platform"""
        return {GuiItemFlag.WHITELISTED: [game for game in self.stats[GuiItemFlag.WHITELISTED] if game.platform == platform],
                GuiItemFlag.BLACKLISTED: [game for game in self.stats[GuiItemFlag.BLACKLISTED] if game.platform == platform],
                GuiItemFlag.INDEXED: [game for game in self.stats[GuiItemFlag.INDEXED] if game.platform == platform]}

    @property
    def steam_folder(self) -> str:
        """Getter for _steam_folder"""
        return self._steam_folder

    def add_steam_folder(self, path) -> None:
        """
        Setter for steam_folder

        Removes any existing steam folder entry from win_platforms,
        then adds itself to win_platforms.
        """
        self.remove_folder(self._steam_folder)
        self._steam_folder = path

        # TODO: A neater way to do this
        steam_platform = PLATFORMS.copy()['win']
        steam_platform.flag = PlatformFlag.STEAM
        # END_TODO
        self.platforms.update({path: steam_platform})


    def remove_steam_folder(self) -> None:
        """Deleter for steam_folder"""
        c = self._steam_folder
        self._steam_folder = ''
        # Delete after to trigger self._platform_changes_made
        self.remove_folder(c)
