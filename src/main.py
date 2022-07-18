from rom_detective import ROOT_FOLDER, initialize_folder
from rom_detective.rom_detective import RomDetective

# TODO: GUI and plonk things into a class
# TODO: Load from a .conf, created by a GUI
# TODO: compare logs to current run in order to update shortcuts, delete missing, etc.
# TODO: Replace winshell/win32com modules
# TODO: Write new tests
WRITE_LOG = True
ROM_FOLDER = r'S:\ROMs'
STEAM_FOLDER = r'C:\Program Files (x86)\Steam'


def main():
    initialize_folder()
    print("Note: You may need to run this application as admin if symlinks aren't being created")

    rd = RomDetective()
    rd.add_rom_folder(r'S:\ROMs')
    rd.add_steam_folder(r'C:\Program Files (x86)\Steam')

    rd.index_all()
    rd.create_shortcuts(dry_run=False)

    if WRITE_LOG:
        rd.logger.write(path_dir=f'{ROOT_FOLDER}\\logs')
    input("Press enter key to exit.")


if __name__ == '__main__':
    main()
