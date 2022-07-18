import os
import glob

import rom_detective.platforms as platforms
from rom_detective.const import PLATFORMS


def scan_for_files(directory: str, extensions: list, recursive: bool = True) -> list[str]:
    """
    Takes a directory path to scan files from
    Returns abspath to ALL files matching any extension from a list of extensions
    """
    path = f'{directory}\\**/*.*' if recursive else f'{directory}\\*.*'
    return [file for file in glob.glob(path, recursive=recursive)
            if os.path.splitext(file)[1] in extensions]


def list_subfolders(directory: str, children: int = 2) -> list[str]:
    """
    Takes a root directory path and iterates through <int> amount
    of children and returns a list of abs-paths
    """
    output = list()
    layer = list([directory])
    for i in range(children):
        result = list()
        for directory in layer:
            result += [f'{directory}\\{subdir}' for subdir in next(os.walk(directory))[1]]
        output += result
        layer = result.copy()
    return output


def identify_platforms_from_path(path: str) -> dict[platforms.Platform]:
    """
    Returns a dict of platforms for every directory in the given path that
    matches any of the alias entries in 'data/platforms.yaml'

    Format: {path: Platform}
    """
    return {directory: platforms.identify_platform_from_path(directory, platforms=PLATFORMS)
            for directory in list_subfolders(path, children=1)
            if platforms.identify_platform_from_path(directory, platforms=PLATFORMS)}
