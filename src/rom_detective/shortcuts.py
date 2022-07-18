__all__ = ['create_shortcut', 'get_destination_folder']

import os
from pathlib import Path

from rom_detective import DEFAULT_TARGET_FOLDER
from rom_detective.item import Item
from rom_detective.platforms import Platform
from rom_detective.logger import LoggerFlag


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
                   true: does not create any folders
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

    # Create ROMs directory if it does not exist AND no destination folder is manually specified
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
    Takes a target_file path and a destination_file and creates an internet shortcut
    Returns string: f'{destination_file}-->{target_file}'
    """
    with open(destination_file, 'w+', encoding="utf-8") as shortcut:
        shortcut.write("[InternetShortcut]\n")
        shortcut.write(f'{target_file}\n')

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


def create_shortcut(item: Item, target_folder: str = '',
                    fullname: bool = True, dry_run: bool = False) -> dict:
    """
    Takes an Item object and the target_folder for where to store all shortcuts,
    then creates a shortcut or symlink from the item source to the target folder

    Returns a dict of either {success:<item>} or {blacklisted:<item>}

    If no target_folder is specified, "%homepath%/ROMs/<platform>" will be used

    Optional flag: fullname: bool (default: True)
                   true: the platform title will be used as the folder name (Nintendo 64)
                   false: the platform id will be used as the folder name (n64)

                   dry_run: bool (default: False)
                   true: simulates creation of folders and shortcuts in terminal
    """
    if item.blacklisted and not item.whitelisted:
        return {LoggerFlag.BLACKLIST: f'{item.source} [{item.filename}]'}

    destination = get_destination_folder(item.filename, item.platform, target_folder=target_folder,
                                         fullname=fullname, dry_run=dry_run)

    # Dry run - don't create symlinks
    if dry_run:
        return {LoggerFlag.DRY_RUN: f'{destination}->{item.source}'}

    if item.extension == '.url':
        return _create_shortcut(target_file=item.source, destination_file=destination)
    else:
        return _create_symlink(target_file=item.source, destination_file=destination)
