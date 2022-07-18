from rom_detective._const_ import ROOT_FOLDER
from rom_detective.startup import init_folders
from rom_detective.class_gui import RomDetectiveGui

# TODO: GUI and plonk things into a class
# TODO: Load from a .conf, created by a GUI
# TODO: compare logs to current run in order to update shortcuts, delete missing, etc.
WRITE_LOG = True
ROM_FOLDER = r'S:\ROMs'
STEAM_FOLDER = r'C:\Program Files (x86)\Steam'


def main():
    print("Note: You may need to run this application as admin if symlinks aren't being created")

    gui = RomDetectiveGui()
    gui.add_rom_folder(r'S:\ROMs')
    gui.add_steam_folder(r'C:\Program Files (x86)\Steam')

    gui.index_all()
    gui.create_shortcuts(dry_run=False)

    if WRITE_LOG:
        gui.logger.write(path_dir=f'{ROOT_FOLDER}\\logs')
    input("Press enter key to exit.")


if __name__ == '__main__':
    init_folders(path=ROOT_FOLDER)
    main()
