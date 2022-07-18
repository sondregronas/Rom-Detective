from dataclasses import dataclass, field

from rom_detective._globals_ import PLATFORMS
from rom_detective._const_ import ROOT_FOLDER

from rom_detective.class_logger import Logger, LoggerFlag
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

from rom_detective.util_shortcuts import create_shortcut


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
    logger: Logger = field(init=False, default=Logger())
    platforms: dict[str, Platform] = field(init=False, default_factory=dict)
    games: list[IndexerItem] = field(init=False, default_factory=list)
    stats: dict[str, list] = field(init=False, default_factory=dict)
    is_indexed: bool = field(init=False, default=False)
    _steam_folder: str = field(init=False, default_factory=str)

    def load_config(self, path):  # pragma: no cover
        """Perform on load"""
        raise NotImplementedError

    def save_config(self, path):  # pragma: no cover
        """Perform on exit"""
        raise NotImplementedError

    """
    ##########################################
        Internal methods
    """

    @property
    def steam_folder(self) -> str:
        """Getter for _steam_folder"""
        return self._steam_folder

    def _platform_changes_made(self) -> None:
        """Called when changes are made"""

        # Clear platforms from logger, then re-add valid platforms
        self.logger.log[LoggerFlag.PLATFORMS] = list()
        [self.logger.add({LoggerFlag.PLATFORMS: f'{path}->{platform.name}'})
         for path, platform in self.platforms.items() if platform]

        if self.is_indexed:
            self.is_indexed = False
            self._reset_games()
            # TODO: Delete associated items from self.games, without forced re-index of everything
            # self.index_all()
        if self.stats:
            self.update_stats()

    def _reset_games(self):
        """Flushes self.games"""
        del self.games
        self.games = list()

    # TODO: Maybe make this be a button?
    def index_platform_from_path(self, path: str, update_stats=True) -> list[IndexerItem]:
        """Index ROMs/Games from a specific platform"""
        if not self.platforms[path]:
            print(f'{path} is not tied to any platform, skipping')

        # Default ROMs
        if self.platforms[path].flag == PlatformFlag.DEF_ROM:
            self.games += index_roms_from_dict({path: self.platforms[path]})

        # Steam library
        elif self.platforms[path].flag == PlatformFlag.STEAM:
            self.games += index_steam_library(self.steam_folder)

        else:  # pragma: no cover
            raise RuntimeError(f"Couldn't index items ({path}: {self.platforms[path]}")

        # Optional flag to not force an update (called manually by index_all)
        if update_stats:
            self.update_stats()

        return self.games

    def update_stats(self) -> dict:
        """Deletes self.stats, then rebuilds it"""
        del self.stats
        self.stats = dict()
        self.stats[GuiItemFlag.WHITELISTED] = [game for game in self.games if game.whitelisted]
        self.stats[GuiItemFlag.BLACKLISTED] = [game for game in self.games if game.blacklisted and not game.whitelisted]
        self.stats[GuiItemFlag.INDEXED] = [game for game in self.games if not game.blacklisted or game.whitelisted]
        return self.stats

    """
        End Internal methods
    ##########################################
    """

    """
    ##########################################
        Button actions
    """

    def add_rom_folder(self, path: str) -> None:
        """
        Add a new folder and try to identify the platform,
        if none specified, attempt to identify its subdirectories (1 layer)

        If none found - allow user to specify manually. User should also be able to override the platform
        """
        platform = identify_platform_from_path(path)
        if platform:
            platforms = {path: platform}
        else:
            platforms = {path: platform} if platform else identify_platforms_from_path(path)
            platforms = platforms if platforms.values() else {path: None}
        self.platforms.update(platforms)
        self._platform_changes_made()

    def remove_folder(self, path: str) -> None:
        """
        Remove a folder (requires just the path),
        remove any associated platforms/indexed items
        """
        self.platforms.pop(path, None)
        self._platform_changes_made()

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

    def specify_platform(self, path: str, platform: Platform) -> None:
        """Overwrite the platform value for a given path"""
        self.platforms.pop(path, None)
        self.platforms[path] = platform

        self._platform_changes_made()

    def index_all(self) -> None:
        """Index everything and append to self.games, then update stats"""
        self._reset_games()
        [self.index_platform_from_path(path, update_stats=False) for path, platform in self.platforms.items() if platform]
        self.update_stats()
        self.is_indexed = True

    def create_shortcuts(self, dry_run: bool = False):
        """Create shortcuts from self.games, as long as is_indexed == True"""
        # TODO: Tie in the logger class
        if not self.is_indexed:
            print('Cannot scan')
            return
        [self.logger.add(create_shortcut(game, dry_run=dry_run)) for game in self.games]

        # Temp
        print(self.logger)
        # if dry_run:
        #    self.logger.write(path_dir=f'{ROOT_FOLDER}\\logs')

    def index_and_create_shortcuts(self):
        """Indexes all platforms and creates shortcuts for the games"""
        self.index_all()
        self.create_shortcuts()

    """
        End Button actions
    ##########################################
    """

    """
    ##########################################
        Statistics / Console
    """

    def stats_by_platform(self, platform: Platform) -> dict:
        """Get the stats for a given platform"""
        return {GuiItemFlag.WHITELISTED: [game for game in self.stats[GuiItemFlag.WHITELISTED] if game.platform == platform],
                GuiItemFlag.BLACKLISTED: [game for game in self.stats[GuiItemFlag.BLACKLISTED] if game.platform == platform],
                GuiItemFlag.INDEXED: [game for game in self.stats[GuiItemFlag.INDEXED] if game.platform == platform]}

    """
        End Statistics / Console
    ##########################################
    """
