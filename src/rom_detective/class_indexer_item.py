import os
import re

from dataclasses import dataclass, field

from rom_detective.class_indexer_platform import Platform
from rom_detective._const_ import ILLEGAL_CHARACTERS
from rom_detective._const_ import ROOT_FOLDER


"""
ConsoleIndexerItem:
    source: 'str' full path to a ROM or game ('C:\\Games\\n64\\Example (Europe).z64'
    platform: 'Platform' object for the ROM or game (Platform(id='n64'...)
    filename: 'str' The target filename ('Example.z64')
    clean_brackets: 'bool' Whether to remove parentheses and brackets from filename
                    during sanitization (Default: True)
    whitelisted: 'bool' Overwrites blacklist when True
    _blacklist: 'bool': Override for property blacklisted, set by blacklist()

    functions:
        - blacklist(force=True) - Override for default 'blacklisted', defined in blacklist.cfg
        - whitelist(force=True) - Overrides blacklist, defined in whitelist.cfg

    properties:
        - title: returns str of filename, without extension ('Example')
        - extension: returns str of extension, including . ('.z64')
        - blacklisted: returns bool of whether a game is blacklisted

    __post_init__:
        def subclass_init()
        self.filename = self.source.split('\\')[-1] if not self.filename else self.filename
        self.sanitize_filename()
"""


@dataclass
class IndexerItem:
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
            self._blacklist = self.source in open(f'{ROOT_FOLDER}\\config\\blacklist.cfg',
                                                  "r", encoding='utf8').read().split('\n')
        except FileNotFoundError as e:  # pragma: no cover
            print(f'Warning: {e}')
            self.whitelisted = False

    def whitelist(self, force: bool = True) -> None:
        """Override for <blacklisted> (Manually defined)"""
        if force:
            self.whitelisted = force
            return
        try:
            self.whitelisted = self.source in open(f'{ROOT_FOLDER}\\config\\whitelist.cfg',
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
        name = re.sub(f'[{ILLEGAL_CHARACTERS}]*', '', name)

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
