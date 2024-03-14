import sys

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from qt_material import apply_stylesheet

from rom_detective import initialize_folder, DEFAULT_TARGET_FOLDER, ROOT_FOLDER, MEI_FOLDER
from rom_detective.const import PLATFORMS
from rom_detective.platforms import PlatformFlag
from rom_detective.rom_detective import RomDetective

# TODO: compare logs to current run in order to update shortcuts, delete missing, etc.
# TODO: Pretty things up
# TODO: Write new tests


class EmittingStream(QObject):
    text = pyqtSignal(str)

    def write(self, text: object):
        self.text.emit(str(text))


def _create_button(text: str, method: object) -> QPushButton:
    b = QPushButton(text)
    b.pressed.connect(method)
    return b


def _create_terminal(hide=False) -> QTextEdit:
    t = QTextEdit()
    t.setReadOnly(True)
    t.setFontFamily("Courier")
    t.setTextColor(QColor('#fff'))
    t.setFontPointSize(10)
    if hide:
        t.hide()
    return t


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rom Detective")
        self.setWindowIcon(QIcon(f'{MEI_FOLDER}\\main.ico'))
        sys.stdout = EmittingStream(text=self.update_console)
        w, h = 900, 600
        self.resize(w, h)

        l = QGridLayout()

        # Platform & Path selector
        self.selector_path = QComboBox()
        self.selector_path.currentTextChanged.connect(self.select_path)
        self.selector_path.setPlaceholderText('Select ROM folder')

        self.selector_platform = QComboBox()
        self.selector_platform.wheelEvent = lambda event: None
        self.selector_platform.currentTextChanged.connect(self.select_platform)
        self.selector_platform.addItems(['None'] + [p.name for p in PLATFORMS.values()])

        add_folder = _create_button('Add', self.add_rom_folder)
        remove_platform = _create_button('Remove', self.remove_platform)
        list_games = _create_button('Gamelist', self.list_selected_roms)

        l.addWidget(QLabel('Rom Folders'), 0, 0, 1, 1)
        l.addWidget(self.selector_path, 0, 1, 1, 3)
        l.addWidget(self.selector_platform, 0, 4)
        l.addWidget(add_folder, 0, 5)
        l.addWidget(remove_platform, 0, 6)
        l.addWidget(list_games, 0, 7)

        # Steam folder
        self.steam_folder = QLineEdit()
        self.steam_folder.setReadOnly(True)
        self.steam_folder.setPlaceholderText('No Steam folder specified')

        specify_steam_folder = QPushButton('Set')
        specify_steam_folder.pressed.connect(self.set_steam_folder)
        remove_steam_folder = QPushButton('Remove')
        remove_steam_folder.pressed.connect(self.remove_steam_folder)
        list_games = _create_button('Gamelist', self.list_steam_games)

        l.addWidget(QLabel('Steam Folder'), 1, 0)
        l.addWidget(self.steam_folder, 1, 1, 1, 4)
        l.addWidget(specify_steam_folder, 1, 5)
        l.addWidget(remove_steam_folder, 1, 6)
        l.addWidget(list_games, 1, 7)

        # Center console
        self.console = _create_terminal(hide=False)
        self.console.setMinimumWidth(600)
        l.addWidget(self.console, 2, 1, 5, 6)

        # Stats
        self.stats = QLabel('Stats:\n'
                            '0 platforms\n'
                            '0 blacklisted\n')
        self.games_amount = QLabel('0/0 Games total')
        self.games_amount.setStyleSheet('QLabel{font-size: 24px; font-weight: bold;}')

        l.addWidget(self.stats, 6, 0)
        l.addWidget(self.games_amount, 9, 0, 1, 3)

        # Destination path
        self.target_folder = QLineEdit()
        self.target_folder.setReadOnly(True)
        self.target_folder.setPlaceholderText('ERR: NOT SPECIFIED')

        set_target_folder = _create_button('Set', self.set_target_folder)
        reset_target_folder = _create_button('Reset', self.reset_target_folder)
        enable_devmode_link = _create_button('URL: Enable\nDevmode', self.open_dev_url)

        l.addWidget(QLabel('Destination'), 7, 0)
        l.addWidget(self.target_folder, 7, 1, 1, 4)
        l.addWidget(set_target_folder, 7, 5)
        l.addWidget(reset_target_folder, 7, 6)
        l.addWidget(enable_devmode_link, 7, 7)

        # Bottom row
        spacer = QFrame()
        spacer.setFixedHeight(3)
        l.addWidget(spacer, 8, 0, 1, 8)

        list_games = _create_button('List all', self.list_all_games)
        list_blacklist = _create_button('List blacklist', self.list_all_blacklist)
        create_shortcuts = _create_button('Create\nshortcuts', self.create_shortcuts)

        l.addWidget(list_games, 9, 5)
        l.addWidget(list_blacklist, 9, 6)
        l.addWidget(create_shortcuts, 9, 7)

        # Start app
        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)
        self.show()

        self.rd = RomDetective
        self.rd_init()

    def open_dev_url(self):
        QDesktopServices.openUrl(QUrl('https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/'))

    @property
    def selected_path(self):
        return ''.join(self.selector_path.currentText().split(' [')[:-1])

    def print_game_list(self, games: list[any], blacklist: bool = False):
        if not games and not blacklist:
            print('Info: No games.')
            return
        if not games and blacklist:
            print('Info: Nothing blacklisted')
            return
        for game in games:
            c_platform = QColor('#ff0e0e')
            c_title = QColor('#fff')
            c_brackets = QColor('#0099ff')
            c_source = QColor('#7e7eff')
            self.console.setTextColor(c_platform)
            self.console.insertPlainText(f'[{game.platform.id}]')

            self.console.setTextColor(c_title)
            self.console.insertPlainText(f': {game.title}')

            if blacklist:
                self.console.setTextColor(c_brackets)
                self.console.insertPlainText(f' ["')
                self.console.setTextColor(c_source)
                self.console.insertPlainText(f'{game.source}')
                self.console.setTextColor(c_brackets)
                self.console.insertPlainText(f'"]')

            self.console.setTextColor(QColor('#fff'))
            self.console.insertPlainText('\n')
            self.console.ensureCursorVisible()

    def confirm_prompt(self, title, text):
        confirm = QMessageBox()
        confirm.setWindowIcon(self.windowIcon())
        confirm.setWindowTitle(title)
        confirm.setIcon(QMessageBox.Icon.Critical)
        confirm.setText(text)
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        return True if confirm.exec() == QMessageBox.StandardButton.Yes else False

    def rd_init(self):
        self.rd = RomDetective()
        if initialize_folder():
            try:
                self.rd.load_config()
            except Warning as e:
                print(f'Warning: {e}')
        if self.rd.platforms:
            print(f'Info: Loaded {len(self.rd.platforms)} platforms from config')
            self.update_paths()
        if self.rd.steam_folder:
            self.steam_folder.setText(self.rd.steam_folder)
        if self.rd.target_folder:
            self.target_folder.setText(self.rd.target_folder)

    def index_all(self):
        if not self.rd.is_indexed:
            self.rd.index_all()
            print(f'Info: {len(self.rd.games)} games found over {len(self.rd.platforms)} platforms.')

            # TODO: Make property of Rom Detective
            normal = [game for game in self.rd.games if not game.blacklisted or game.whitelisted]
            blacklisted = [game for game in self.rd.games if game.blacklisted and not game.whitelisted]

            self.stats.setText(f'Stats:\n'
                               f'{len(self.rd.platforms)} platforms\n'
                               f'{len(blacklisted)} blacklisted\n')
            self.games_amount.setText(f'{len(normal)}/{len(self.rd.games)} Games total')
            self.rd.save_config()

    def list_all_blacklist(self):
        games = [game for game in self.rd.games if game.blacklisted and not game.whitelisted]
        print('Info: All blacklisted items')
        self.print_game_list(games, blacklist=True)
        print('Info: End all blacklisted items')

    def list_all_games(self):
        if not self.rd.games:
            print(f'Warning: No games found')
            return
        games = [game for game in self.rd.games if not game.blacklisted or game.whitelisted]
        print(f'Info: Listing all games')
        self.print_game_list(games)
        print('Info: End of list')
        self.list_all_blacklist()

    def list_selected_roms(self):
        if self.selected_path not in self.rd.platforms.keys():
            print(f'Warning: Cannot display gamelist for selected path')
            return
        games = [game for game in self.rd.games
                 if (not game.blacklisted or game.whitelisted)
                 and self.selected_path in game.source]
        if not games:
            print(f'Warning: No games found from {self.selected_path}')
            return
        print(f'Info: Listing ROMs in {self.selected_path} ({len(games)})')
        self.print_game_list(games)
        print('Info: End of list')
        self._list_blacklist_selected_roms()

    def list_steam_games(self):
        if not self.rd.steam_folder:
            print(f'Warning: Steam folder not specified')
            return
        games = [game for game in self.rd.games
                 if (not game.blacklisted or game.whitelisted)
                 and game.platform.flag == PlatformFlag.STEAM]
        if not games:
            print('Warning: No games found from Steam')
            return
        print(f'Info: Listing games in Steam ({len(games)})')
        self.print_game_list(games)
        print('Info: End of Steam gameslist')
        self._list_blacklist_steam()

    def _list_blacklist_selected_roms(self):
        if self.selected_path not in self.rd.platforms.keys():
            print(f'Warning: Cannot display blacklist for selected path')
            return
        games = [game for game in self.rd.games
                 if game.blacklisted and not game.whitelisted
                 and self.rd.platforms[self.selected_path] == game.platform]
        if not games:
            return
        print(f'Blacklisted items in {self.selected_path} ({len(games)})')
        self.print_game_list(games, blacklist=True)
        print('End blacklist.')

    def _list_blacklist_steam(self):
        if not self.rd.steam_folder:
            print(f'Warning: Cannot display blacklist for Steam')
            return
        games = [game
                 for game in self.rd.games
                 if game.blacklisted and not game.whitelisted
                 and game.platform.flag == PlatformFlag.STEAM]
        if not games:
            return
        print(f'Blacklisted items for Steam ({len(games)})')
        self.print_game_list(games, blacklist=True)
        print('End blacklist.')

    def dry_run(self):
        self.index_all()
        print('Info: Simulated output, logs are not actually written')
        self.rd.create_shortcuts(dry_run=True)

    def create_shortcuts(self):
        self.index_all()
        self.rd.create_shortcuts(dry_run=False)

    def add_rom_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select ROMs or platform folder').replace('/', '\\')
        if folder:
            self.rd.add_rom_folder(folder)
            self.update_paths()
            self.selector_path.setCurrentIndex(self.selector_path.count()-1)

    def set_target_folder(self, path: str = None):
        p = QFileDialog.getExistingDirectory(self, 'Select Folder').replace('/', '\\') if not path else path
        if p:
            self.rd.target_folder = p
            self.target_folder.setText(self.rd.target_folder)
            print(f'Info: Set target folder to {self.rd.target_folder}')
            self.rd.save_config()

    def reset_target_folder(self):
        if self.confirm_prompt(title='Confirm target folder', text=f'Reset target folder to\n'
                                                                   f'"{DEFAULT_TARGET_FOLDER}"'):
            self.set_target_folder(path=DEFAULT_TARGET_FOLDER)

    def set_steam_folder(self):
        p = QFileDialog.getExistingDirectory(self, 'Select Steam Folder').replace('/', '\\')
        if p:
            self.rd.add_steam_folder(p)
            self.steam_folder.setText(self.rd.steam_folder)
            print(f'Info: Set Steam folder to {self.rd.steam_folder}')
            self.index_all()

    def remove_steam_folder(self):
        if self.steam_folder and self.confirm_prompt('Confirm removal', 'Remove Steam folder?'):
            self.rd.remove_steam_folder()
            self.steam_folder.setText(self.rd.steam_folder)
            print(f'Info: Removed Steam folder')

    def print_target_folder(self):
        print(f'Target folder: {self.rd.target_folder}')

    def update_paths(self):
        """Update platformlist on change"""
        paths = [''.join(self.selector_path.itemText(i).split(' [')[:-1])  # Get all paths from selector (excl. [<id>])
                 for i in reversed(range(self.selector_path.count()))]  # And add them to a list

        for path, platform in self.rd.platforms.items():
            if path not in paths:  # If path isn't in the selector list, assume it is new
                if hasattr(platform, 'flag') and platform.flag == PlatformFlag.STEAM:  # Don't add STEAM platforms
                    continue
                p_id = platform.id if hasattr(platform, 'id') else 'None'  # Get platform ID, None if invalid
                self.selector_path.addItem(f'{path} [{p_id}]')  # Add item with platform ID identifier
        self.index_all()

    def select_path(self, text):
        """Updates selector_platform to match value of selected path"""
        p = self.rd.platforms[self.selected_path]  # Get platform
        p_name = p.name if hasattr(p, 'name') else 'None'  # Extract name from platform, unless platform is None
        self.selector_platform.setCurrentText(p_name)  # Update selector_platform to platform.name

    def select_platform(self, text):
        """Updates platform on the selected path"""
        if not self.selected_path:  # Will crash if there's no path selected
            return
        new_platform = None if text == 'None' else [p for p in PLATFORMS.values() if p.name == text][0]  # Get platform from name
        p_id = new_platform.id if hasattr(new_platform, 'id') else 'None'  # Get ID from platform
        if not hasattr(self.rd.platforms[self.selected_path], 'id') or self.rd.platforms[self.selected_path].id != p_id:
            self.rd.specify_platform(self.selected_path, new_platform)  # Update platform in Rom Detective
            self.index_all()
        self.selector_path.setItemText(self.selector_path.currentIndex(), f'{self.selected_path} [{p_id}]')  # Update label for path

    def remove_platform(self):
        if not self.selected_path:  # Will crash if there's no path selected
            return
        if self.confirm_prompt('Confirm removal', f'Remove {self.selected_path}?'):
            self.rd.remove_folder(self.selected_path)
            # TODO BUG: Causes crash if last item gets removed
            self.selector_path.removeItem(self.selector_path.currentIndex())
            self.index_all()

    def update_console(self, text):
        """Append text to the QTextEdit."""
        color = '#fff'
        c_warning = '#ff00ff'
        c_info = '#0099ff'
        if text.lower().startswith('warning'): color = c_warning
        elif text.lower().startswith('info'): color = c_info
        elif text.lower().startswith('blacklist'): color = c_info
        self.console.setTextColor(QColor(color))
        self.console.insertPlainText(text)
        self.console.ensureCursorVisible()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    apply_stylesheet(app, theme='dark_amber.xml')

    app.exec()

    # Restore sys.stdout
    sys.stdout = sys.__stdout__
