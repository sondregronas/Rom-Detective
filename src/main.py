####################################
# IMPORTS FOR PYINSTALLER
# Todo: move this
import os
import re
import vdf
import yaml
import winshell

from pathlib import Path
from xml.dom import minidom
from dataclasses import dataclass
from win32com.client import Dispatch
####################################

from rom_detective.util_main import identify_platforms_from_path, index_roms_from_dict
from rom_detective.util_index import index_steam_library
from rom_detective._globals_ import PLATFORMS
from rom_detective._const_ import ROOT_FOLDER
from rom_detective.util_shortcuts import create_shortcut
from rom_detective.class_logger import Logger
from startup import init_folders


# TODO: GUI and plonk things into a class
# TODO: Load from a .conf, created by a GUI
# TODO: compare logs to current run in order to update shortcuts, delete missing, etc.
WRITE_LOG = True
ROM_FOLDER = r'S:\ROMs'
STEAM_FOLDER = r'C:\Program Files (x86)\Steam'

def main():
    print("Note: You may need to run this application as admin if symlinks aren't being created")

    init_folders(path=ROOT_FOLDER)
    logger = Logger()
    # Identify platforms in main_folder
    rom_folders = identify_platforms_from_path(ROM_FOLDER)

    [logger.add({'platforms': f'{path}->{rom_folders[path].name}'}) for path in rom_folders]

    """
    # Overwrite / add items / set to None to filter out
    rom_folders.update({r'S:\ROMs\n64': PLATFORMS['n64']})
    # Don't include entries by setting them to None, instead of removing:
    rom_folders.update({r'S:\ROMs\wiiu': None})
    """

    # Index all ROMs in rom_folders
    games = index_roms_from_dict(rom_folders)

    # TODO: add non-roms (windows titles) to 'platforms' in logger automagically
    games += index_steam_library(STEAM_FOLDER)
    logger.add({'platforms': f'{STEAM_FOLDER}->{PLATFORMS["win"].name}'})
    ##

    # Create shortcuts for all entries in games
    [logger.add(create_shortcut(game, dry_run=False)) for game in games]

    # Finish up
    print(logger)
    if WRITE_LOG:
        logger.write(path_dir=f'{ROOT_FOLDER}\\logs')
    input("Press enter key to exit...")


if __name__ == '__main__':
    main()
