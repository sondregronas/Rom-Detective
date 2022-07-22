"""Game and ROM Shortcuts Manager by @sondregronas"""

import os.path
import sys
from pathlib import Path

# Default: %homepath%\\roms for the running user
DEFAULT_TARGET_FOLDER = f'{Path.home()}\\ROMs'
ILLEGAL_CHARACTERS = ':®©™*"–/|<>?!'

ROOT_FOLDER = os.path.dirname(sys.executable) \
    if getattr(sys, 'frozen', False) \
    else (Path(os.path.abspath(__file__)).parents[2])

MEI_FOLDER = sys._MEIPASS if hasattr(sys, '_MEIPASS') else ROOT_FOLDER
DATA_FOLDER = f'{MEI_FOLDER}\\data'
CONF_FOLDER = f'{ROOT_FOLDER}\\config'
LOGS_FOLDER = f'{ROOT_FOLDER}\\logs'


def initialize_folder(path: str = ROOT_FOLDER) -> bool:
    """
    Spawn relevant files and folders upon startup, if they don't already exist
    (config directory and files and logs directory)

    Returns False if config file did not exist
    """
    first_run = True

    if not Path(path).exists():
        raise RuntimeError(f'{path} is not a valid folder for initialization.')

    config_folder = Path(f'{path}\\config')
    logs_folder = Path(f'{path}\\logs')

    # CONFIG FILES
    if not config_folder.exists():
        config_folder.mkdir(exist_ok=True)

    # LOGS
    if not logs_folder.exists():
        logs_folder.mkdir(exist_ok=True)

    blacklist_cfg = Path(f'{config_folder}\\blacklist.cfg')
    blacklist_cfg_content = (
        "# Path to ROMs or games that weren't invited.\n"
        "# Example:\n"""
        "# C:\\ROMs\\n64\\My Rom File.z64\""
    )

    whitelist_cfg = Path(f'{config_folder}\\whitelist.cfg')
    whitelist_cfg_content = (
        "# Path to ROMs or games that originally weren't allowed in, but allowed in by you. (Copy the source from blacklist)\n"
        "# Example:\n"""
        "# C:\\ROMs\\n64\\My Rom File.z64\""
    )

    config_cfg = Path(f'{config_folder}\\config.cfg')
    config_cfg_content = (
        "# Empty for now. To be implemented.\n"
    )

    if not blacklist_cfg.exists():
        open(blacklist_cfg, 'w+').write(blacklist_cfg_content)
    if not whitelist_cfg.exists():
        open(whitelist_cfg, 'w+').write(whitelist_cfg_content)
    if not config_cfg.exists():
        first_run = False
        open(config_cfg, 'w+').write(config_cfg_content)

    return first_run
