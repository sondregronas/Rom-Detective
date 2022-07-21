<div align="center">
<h1>🕵️ Rom Detective 🕹️</h1>
<img src="media/graphic.png" width="50%">

<a href="https://github.com/sondregronas/Rom-Detective/"><img src="https://img.shields.io/github/workflow/status/sondregronas/Rom-Detective/CI"></a>
<a href="https://github.com/sondregronas/Rom-Detective/commit/"><img src="https://img.shields.io/github/last-commit/sondregronas/Rom-Detective"></a>
<img src="https://img.shields.io/github/license/sondregronas/Rom-Detective">
<a href="https://codecov.io/gh/sondregronas/Rom-Detective" ><img src="https://codecov.io/gh/sondregronas/Rom-Detective/branch/main/graph/badge.svg?token=HF8EDCQ4KZ"/></a>
<a href="https://www.buymeacoffee.com/u92RMis"><img src="https://badgen.net/badge/icon/buymeacoffee?icon=buymeacoffee&label"></a>

<br>

A tool to automatically *index* ROMs and create shortcuts to them. Allowing you to physically store your ROMs wherever you'd like, while still treating them like individual ROMs for launchers like LaunchBox.

**Now with a GUI, though it might not be the most intuitive**
</div>

## How
The application only works on Windows. The destination drive must be formatted to support symlinks for ROMs (NTFS or UDF, see https://docs.microsoft.com/en-us/windows/win32/fileio/filesystem-functionality-comparison)

Your system must either have [Developer Mode enabled](https://blogs.windows.com/windowsdeveloper/2016/12/02/symlinks-windows-10/) or the application must be run as admin.

Add your ROM folder (or individual folders) and hit "Create Shortcuts" - and you're off to the races (Images coming soon)

## What
ROMs or Games are indexed as a `IndexerItem` dataclass:
```python
@dataclass
class IndexerItem:
    source: str  # Path to original ROM or Game file/executable
    platform: Platform  # Global variable PLATFORMS[<platform_id>] (PLATFORMS['n64'])
    filename: str  # Does some re-formatting and searching, but it's not an indexer for all ROM types.
    title: str  # Same as filename, but without an extension
```

`IndexerItem` has different subclasses for certain ROM or game types to automatically fetch the correct ROM file and metadata:
```python
PS3IndexItem(IndexerItem)  # Targets <folder>\PS3_GAME\USRDIR\EBOOT.BIN and gets title from a database
WiiUIndexItem(IndexerItem)  # Reads a meta.xml for any given *.rpx file, also blacklists DLC or Update directories
SteamLibraryIndexItem(IndexerItem)  # Reads libraryfolders.vdf in primary steam installation folder and gets installed games (blacklists software)
```

`Platform` objects get derived from `data/platforms.yaml`.

## Why?
In order to more easily update the library inside an emulation launcher (such as LaunchBox),
proper naming schemes & file structure is key for good results, but not always permitted depending on the ROM type.

Some ROMs require specific naming schemes to work at all, such as Playstation 3's `EBOOT.BIN` ROMs.
By creating a shortcut to `EBOOT.BIN` using the proper game title as the filename will however allow LaunchBox to interpret the ROM correctly.

This also allows LaunchBox to watch for added/removed ROMs, without physically having to move the ROM files, meaning they can be stored wherever without losing that benefit.

## Manual build:
```bash
pip install -r requirements.txt
pyinstaller main.spec
```

Note: if your files are stored on a NAS and you're running as admin, make sure the system user on your PC has access to the network drives (see `run.bat`) (Or just enable devmode and run as a normal user)
## TO-DO:
- Complete platforms / default extensions in `src/const.py`
- Tidy up UI, write tests
- Watch for new/deleted ROMs & update automatically (compare log to console)
