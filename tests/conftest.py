import sys
import pytest

from tests import *


# Make sure that the application source directory (this directory's parent) is on sys.path.
sys.path.insert(0, f'{ROOT_FOLDER}\\src')


def pytest_addoption(parser):
    parser.addoption("--create-files", action="store_true", default=False, help="allow tests to write files")


def pytest_configure(config):
    config.addinivalue_line("markers", "createfiles: use --create-files flag to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--create-files"):
        return
    skip = pytest.mark.skip(reason="need --create-files option to run")
    [item.add_marker(skip) for item in items if "createfiles" in item.keywords]
