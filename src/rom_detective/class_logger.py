from rom_detective._const_ import ROOT_FOLDER


class Logger:
    """
    A logger for Rom Detective
    Holds logs in a dict with 4 key values:

    From create_shortcut:
        'blacklist': list() -> list of items that have not been processed blacklisted ({source})
        'success' or 'dry_run': list() -> list of items that were succesful ({shortcut}->{source})

    From platforms:
        'platforms': list() -> list of ({platform_source}->{platform_name})
    """
    def __init__(self):
        # TODO: Change keys to enum values?
        self.log = dict({
            'blacklist': list(),
            'success': list(),
            'dry_run': list(),
            'platforms': list(),
        })
        self.log_files: dict = dict({
            'blacklist': 'blacklist.log',
            'success': 'active_shortcuts.log',
            'platforms': 'platforms.log'
            # 'dry_run': 'dev_dry_run.log'
        })

    def add(self, entry: dict) -> None:
        """Add an entry to the log, takes a dict of {<log_type>: string}"""
        self.log[list(entry.keys())[0]] += [entry[list(entry.keys())[0]]]

    @property
    def successful(self):
        """Returns amount of lines in success or dry_run"""
        return len(self.log['success']) + len(self.log['dry_run'])

    @property
    def blacklisted(self):
        """Returns amount of blacklisted items"""
        return len(self.log['blacklist'])

    @property
    def platforms(self):
        """Returns amount of platforms"""
        return len(self.log['platforms'])

    @property
    def total(self):
        """Returns sum of all entries, excluding platforms"""
        return sum([len(self.log[key]) for key in ['blacklist', 'success', 'dry_run']])

    def load(self, path: str) -> None:
        """Load a series of old log files, will be used to compare"""
        raise NotImplementedError

    def write(self, path: str = f'{ROOT_FOLDER}\\logs') -> bool:
        """
        Write (by default: all) logs to disk in the given path

        Returns True if log is written, False if it is skipped
        """
        if not self.log['success'] and self.successful:
            print(f"Would've written {self.successful} entries to active_shortcuts.log\n"
                  f"and {self.blacklisted} entries to blacklist.log (DRY_RUN)")
            return False
        for key, logfile in self.log_files.items():
            target = f'{path}\\{logfile}'
            if key in self.log.keys():
                file = open(target, "w", encoding='utf-8')
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
