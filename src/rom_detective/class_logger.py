from rom_detective._const_ import ROOT_FOLDER


class Logger:
    def __init__(self):
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
        self.log[list(entry.keys())[0]] += [entry[list(entry.keys())[0]]]

    @property
    def successful(self):
        return len(self.log['success']) + len(self.log['dry_run'])

    @property
    def blacklisted(self):
        return len(self.log['blacklist'])

    @property
    def platforms(self):
        return len(self.log['platforms'])

    @property
    def total(self):
        return sum([len(self.log[key]) for key in self.log])

    def load(self, path: str) -> None:
        raise NotImplementedError

    def write(self, path: str = ROOT_FOLDER) -> bool:
        """Returns True if log is written, False if it is skipped"""
        if not self.log['success'] and self.successful:
            print(f"Would've written {self.successful} entries to active_shortcuts.log\n"
                  f"and {self.blacklisted} entries to blacklist.log (DRY_RUN)")
            return False
        for key, logfile in self.log_files.items():
            target = f'{path}\\{logfile}'
            print(target)
            if key in self.log.keys():
                print(key)
                file = open(target, "w", encoding='utf-8')
                file.write('\n'.join(self.log[key]))
                file.close()
        return True

    def __str__(self):
        return f"\n" \
               f"================================================================\n" \
               f"Log results:\n" \
               f"================================================================\n" \
               f"Blacklisted games: {self.blacklisted}, see logs/blacklist.log for details\n" \
               f"Successful games: {self.successful}, see logs/active_shortcuts.log for details\n" \
               f"Sum of indexed games: {self.total} over {self.platforms} platforms.\n" \
               f"================================================================\n"
