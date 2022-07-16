import os
from pathlib import Path

# Test variables
# TEST_ROOT_PATH = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}'
ROOT_FOLDER = (Path(os.path.abspath(__file__)).parents[1])
TEST_FILES_PATH = f'{ROOT_FOLDER}\\tests\\test_files'
TEST_ROMS_PATH = f'{TEST_FILES_PATH}\\roms'
