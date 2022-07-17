__all__ = ['create_shortcut', 'get_destination_folder']

import os

from pathlib import Path
from win32com.client import Dispatch

from rom_detective.class_indexer_item import IndexerItem
from rom_detective.class_indexer_platform import Platform, PlatformFlag
from rom_detective._const_ import DEFAULT_TARGET_FOLDER
from rom_detective.class_logger import LoggerFlag


def get_destination_folder(title: str, platform: Platform, target_folder: str = '',
                           fullname: bool = True, dry_run: bool = False) -> str:
    """
    Takes a title: str, platform: Platform and optionally a target_folder
    If target_folder is not specified, use DEFAULT_TARGET_FOLDER

    Returns a destination path for a shortcut for the corresponding platform
    Format: <target_folder>\\<platform_name>\\<title>

    Optional flag: fullname: bool (default: True)
                   true: the platform title will be used as the folder name (Nintendo 64)
                   false: the platform id will be used as the folder name (n64)

                   dry_run: bool (default: False)
                   true: simulates creation of folders in terminal
    """
    destination = target_folder

    default_location = False
    # If no destination folder is specified, use the default folder (%homepath%/ROMs)
    if not destination or destination == DEFAULT_TARGET_FOLDER:
        default_location = True
        destination = DEFAULT_TARGET_FOLDER

    # Append platform folder and title, fullname defines full platform name, or the shorthand (Windows | win)
    destination += f'\\{platform.name}\\{title}' if fullname else f'\\{platform.id}\\{title}'

    if dry_run:
        return destination

    # Create ROMs directory if it does not exist AND no destination folder is specified
    if not os.path.exists(Path(destination).parents[1]) and default_location:
        print(f'Created directory {Path(destination).parents[1]}')
        os.makedirs(Path(destination).parent)

    # Verify that platform parent directory exists. If platform directory does not exist, create it
    if os.path.exists(Path(destination).parents[1]) and not os.path.exists(Path(destination).parent):
        print(f'Created directory {Path(destination).parent}')
        os.makedirs(Path(destination).parent)

    return destination


def _create_shortcut(target_file: str, destination_file: str) -> dict:
    """
    Takes a target_file path and a destination_file and creates a shortcut
    Returns string: f'{destination_file}-->{target_file}'

    If shortcut_destination has a .url file extension, an internet shortcut is created
    if not, a .lnk shortcut is created
    """
    if destination_file.endswith('.url'):
        with open(destination_file, 'w+', encoding="utf-8") as shortcut:
            shortcut.write("[InternetShortcut]\n")
            shortcut.write(f'{target_file}\n')
    else:
        if not destination_file.endswith('.lnk'):
            destination_file += '.lnk'
        # TODO: Replace Dispatch?
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(destination_file)
        shortcut.Targetpath = target_file
        shortcut.save()
    return {LoggerFlag.SUCCESS: f'{destination_file}->{target_file}'}


def _create_symlink(target_file: str, destination_file: str) -> dict:
    """
    Takes a target_file path and a destination_file and creates a symlink
    Returns dict: 'success':f'{destination_file}->{target_file}'

    Symlinks may require special privileges, which will raise a RuntimeError
    """
    try:
        os.symlink(target_file, destination_file)
    except FileExistsError:
        # TODO: Overwrite? incase target_file has changed location
        print(f'Shortcut already exists for {target_file}, skipping')
    except OSError as e:  # pragma: no cover
        raise RuntimeError(f'Missing Privileges to create symlinks, try running as admin. (Msg: {e})')
    return {LoggerFlag.SUCCESS: f'{destination_file}->{target_file}'}


def create_shortcut(console_item: IndexerItem, target_folder: str = '',
                    fullname: bool = True, dry_run: bool = False) -> dict:
    """
    Takes a ConsoleIndexerItem object and the target_folder for where to store all shortcuts,
    then creates a shortcut or symlink from the item source to the target folder

    Returns a dict of either {success:<item>} or {blacklisted:<item>}

    If no target_folder is specified, "%homepath%/ROMs/<platform>" will be used

    Optional flag: fullname: bool (default: True)
                   true: the platform title will be used as the folder name (Nintendo 64)
                   false: the platform id will be used as the folder name (n64)

                   dry_run: bool (default: False)
                   true: simulates creation of folders and shortcuts in terminal
    """
    if console_item.blacklisted and not console_item.whitelisted:
        return {LoggerFlag.BLACKLIST: f'{console_item.source} [{console_item.filename}]'}

    methods = {
        PlatformFlag.STEAM: _create_shortcut,
        PlatformFlag.DEF_ROM: _create_symlink
    }

    destination = get_destination_folder(console_item.filename, console_item.platform, target_folder=target_folder,
                                         fullname=fullname, dry_run=dry_run)

    # Dry run - don't create symlinks
    if dry_run:
        return {LoggerFlag.DRY_RUN: f'{destination}->{console_item.source}'}

    return methods[console_item.platform.flag](target_file=console_item.source, destination_file=destination)
