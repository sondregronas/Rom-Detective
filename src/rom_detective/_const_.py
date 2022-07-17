import os
import sys
import winshell

from pathlib import Path

# Default: %homepath%\\roms for the running user
DEFAULT_TARGET_FOLDER = f'{winshell.folder("profile")}\\ROMs'

# Constants
ILLEGAL_CHARACTERS = ':®©™*"–/|<>?!'

# ROOT_FOLDER
if getattr(sys, 'frozen', False):
    ROOT_FOLDER = os.path.dirname(sys.executable)  # pragma: no cover
else:
    ROOT_FOLDER = (Path(os.path.abspath(__file__)).parents[2])

# Database location
DATA_FOLDER = f'{ROOT_FOLDER}\\data'
