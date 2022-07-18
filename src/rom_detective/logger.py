from pathlib import Path
from dataclasses import dataclass


@dataclass
class LoggerFlag:
    SUCCESS = 'success'
    BLACKLIST = 'blacklist'
    DRY_RUN = 'dry_run'
    PLATFORMS = 'platforms'


"""
Logger
======
A logger for Rom Detective
Holds logs in a dict with 4 key values:

From create_shortcut:
    'blacklist': list() -> list of items that have not been processed blacklisted ({source})
    'success' or 'dry_run': list() -> list of items that were successful ({shortcut}->{source})

From platforms:
    'platforms': list() -> list of ({platform_source}->{platform_name})
"""


class Logger:
    """Logger Class"""
    def __init__(self):
        self.log = dict({
            LoggerFlag.BLACKLIST: list(),
            LoggerFlag.SUCCESS: list(),
            LoggerFlag.DRY_RUN: list(),
            LoggerFlag.PLATFORMS: list(),
        })
        self.log_files: dict = dict({
            LoggerFlag.BLACKLIST: 'blacklist.log',
            LoggerFlag.SUCCESS: 'active_shortcuts.log',
            LoggerFlag.DRY_RUN: 'platforms.log',
        })

    def add(self, entry: dict) -> None:
        """Add an entry to the log, takes a dict of {<log_type>: string}"""
        self.log[list(entry.keys())[0]] += [entry.values()]

    @property
    def successful(self) -> int:
        """Returns amount of lines in success or dry_run"""
        return len(self.log[LoggerFlag.SUCCESS]) + len(self.log[LoggerFlag.DRY_RUN])

    @property
    def blacklisted(self) -> int:
        """Returns amount of blacklisted items"""
        return len(self.log[LoggerFlag.BLACKLIST])

    @property
    def platforms(self) -> int:
        """Returns amount of platforms"""
        return len(self.log[LoggerFlag.PLATFORMS])

    @property
    def total(self) -> int:
        """Returns sum of all entries, excluding platforms"""
        return sum([len(self.log[key]) for key in [LoggerFlag.BLACKLIST, LoggerFlag.SUCCESS, LoggerFlag.DRY_RUN]])

    def load(self, path: str) -> None:
        """Load a series of old log files, will be used to compare"""
        raise NotImplementedError

    def write(self, path_dir: str) -> bool:
        """
        Write (by default: all) logs to disk in the given path

        Returns True if log is written, False if it is skipped
        """
        if len(self.log[LoggerFlag.DRY_RUN]):
            print(f"Would've written {self.successful} entries to active_shortcuts.log\n"
                  f"and {self.blacklisted} entries to blacklist.log (DRY_RUN)")
            return False

        # Create the given folder if it doesn't exist, but parent does
        if Path(path_dir).parent.is_dir():
            if not Path(path_dir).is_dir():
                Path(path_dir).mkdir(exist_ok=True)
        else:
            raise RuntimeError(f'Invalid directory: {Path(path_dir).parent}')

        for key, logfile in self.log_files.items():
            target = f'{path_dir}\\{logfile}'
            if key in self.log.keys():
                file = open(target, "w+", encoding='utf-8')
                file.write('\n'.join(self.log[key]))
                file.close()

        return True

    def __str__(self):
        """String representation in console"""
        return f"\n" \
               f"================================================================\n" \
               f"Log results:\n" \
               f"================================================================\n" \
               f"Blacklisted games: {self.blacklisted}, see logs/blacklist.log for details\n" \
               f"Successful games: {self.successful}, see logs/active_shortcuts.log for details\n" \
               f"Sum of indexed games: {self.total} over {self.platforms} platforms.\n" \
               f"================================================================\n"
