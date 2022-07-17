from dataclasses import dataclass, field

from rom_detective._globals_ import PLATFORMS

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform

from rom_detective.util_main import (
    identify_platform_from_path,
    identify_platforms_from_path,
    index_roms_from_dict,
)
from rom_detective.util_index import (
    index_steam_library,
)


"""
RomDetectiveGui
===============

Functions associated to GUI buttons (To be implemented)

win_platforms = {path: Platform} for every WIN platform entry added (Currently: Steam)
rom_platforms = {path: Platform} for every ROM platform entry added (Derived from platforms.yaml)
games = list[IndexerItems] - ALL indexed games
stats = Every indexed game sorted by whitelisted, blacklisted or indexed: {'whitelisted': list[IndexerItem],
                                                                           'blacklisted': list[IndexerItem],
                                                                           'indexed': list[IndexerItem}}
stats_by_platform(Platform) same as stats, but only for the specified platform (Should maybe be from path?)

add_folder_roms(path) - Adds given path to rom_platforms if a platform is identified,
                        if none identified, try to identify child directories (1 layer)
add_steam_folder(path) - Adds steam folder to win_platforms

specify_platform(path, platform) - forces a platform for given path, reindexes if necessary

remove_steam_folder() -> sets value to None, and calls remove_folder(steam_folder)
remove_folder(path) -> Removes associated platforms

index_platform(platform) -> index only that platform
index_all() -> indexes all platforms, appends to games, updates stats
"""


@dataclass
class RomDetectiveGui:
    win_platforms: dict[str, Platform] = field(default_factory=dict)
    rom_platforms: dict[str, Platform] = field(default_factory=dict)
    games: list[IndexerItem] = field(default_factory=list)
    stats: dict[str, list] = field(default_factory=dict)
    _steam_folder: str = field(default_factory=str)

    @property
    def platforms(self):
        """Returns a dict {path: Platform} for every platform added"""
        return self.win_platforms | self.rom_platforms.copy()

    def add_folder_roms(self, path: str):
        """
        Add a new folder and try to identify the platform,
        if none specified, attempt to identify it's subdirectories (1 layer)

        If none found - allow user to specify manually. User should also be able to override the platform
        """
        platform = identify_platform_from_path(path)
        self.rom_platforms.update({path: platform} if platform else
                                  identify_platforms_from_path(path))
        # TODO: If platform not identified, add just the path and allow user to specify platform

    def _platform_changes_made(self):
        """Called when changes are made"""
        # TODO: Delete associated items from self.games, without forced re-index of everything
        if self.stats:
            self.index_all()
            self.update_stats()

    def remove_folder(self, path: str):
        """
        Remove a folder (requires just the path),
        be sure to remove any associated platforms/indexed items
        """
        self.rom_platforms.pop(path, None)
        self.win_platforms.pop(path, None)

        self._platform_changes_made()

    def specify_platform(self, path: str, platform: Platform):
        """Overwrite the platform value for a given path"""
        self.rom_platforms.pop(path, None)
        self.win_platforms.pop(path, None)

        if platform == PLATFORMS['win']:
            self.win_platforms[path] = platform
        else:
            self.rom_platforms[path] = platform

        self._platform_changes_made()

    def index_platform(self, platform: Platform): # pragma: no cover
        """Index ROMs/Games from a specific platform"""
        if platform != PLATFORMS['win']:
            # TODO
            pass

        raise NotImplementedError

    def index_all(self):
        """Index everything and append to self.games, then update stats"""
        del self.games
        self.games = list()
        self.games += index_roms_from_dict(self.rom_platforms)
        self.games += index_steam_library(self.steam_folder) if self.steam_folder else []
        self.update_stats()

    def update_stats(self) -> dict:
        """Deletes self.stats, then rebuilds it"""
        del self.stats
        self.stats = dict()

        # TODO: Switch to enum?
        self.stats['whitelisted'] = [game for game in self.games if game.whitelisted]
        self.stats['blacklisted'] = [game for game in self.games if game.blacklisted and not game.whitelisted]
        self.stats['indexed'] = [game for game in self.games if not game.blacklisted or game.whitelisted]

        return self.stats

    def stats_by_platform(self, platform: Platform):
        """Get the stats for a given platform"""
        return {'whitelisted': [game for game in self.stats['whitelisted'] if game.platform == platform],
                'blacklisted': [game for game in self.stats['blacklisted'] if game.platform == platform],
                'indexed': [game for game in self.stats['indexed'] if game.platform == platform]}

    @property
    def steam_folder(self):
        """Getter for _steam_folder"""
        return self._steam_folder

    def add_steam_folder(self, path):
        """
        Setter for steam_folder

        Removes any existing steam folder entry from win_platforms,
        then adds itself to win_platforms.
        """
        if self._steam_folder in self.win_platforms.keys():
            del self.win_platforms[self._steam_folder]
        self.win_platforms.update({path: PLATFORMS['win']})
        self.win_platforms = {path: PLATFORMS['win']}
        self._steam_folder = path

        return self._steam_folder

    def remove_steam_folder(self):
        """Deleter for steam_folder"""
        copy = self._steam_folder
        self._steam_folder = ''
        self.remove_folder(copy)
