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
    print("Note: You may need to run this application as admin if symlinks aren't being created")

    rd = RomDetective()

    # Returns True if folders existed
    if initialize_folder():
        try:
            rd.load_config()
        except Warning as e:
            print(e)

    if rd.platforms:
        print(f'Loaded config with {len(rd.platforms)} platforms')
    else:
        rd.add_rom_folder(ROM_FOLDER)
        rd.add_steam_folder(STEAM_FOLDER)

    rd.index_all()
    rd.create_shortcuts(dry_run=False)
    rd.save_config()

    if WRITE_LOG:
        rd.logger.write(path_dir=f'{ROOT_FOLDER}\\logs')
    input("Press enter key to exit.")


if __name__ == '__main__':
    main()
