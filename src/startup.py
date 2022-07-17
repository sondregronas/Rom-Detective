from pathlib import Path


def init_folders(path: str) -> bool:
    if not Path(path).exists():
        raise RuntimeError(f'{path} is not a valid folder for initialization.')

    logs_folder = Path(f'{path}\\logs')
    config_folder = Path(f'{path}\\config')

    # LOGS
    if not logs_folder.exists():
        logs_folder.mkdir(exist_ok=True)

    # CONFIG FILES
    if not config_folder.exists():
        config_folder.mkdir(exist_ok=True)

    blacklist_cfg = Path(f'{config_folder}\\blacklist.cfg')
    blacklist_cfg_content = (
        "# Path to ROMs or games that weren't invited.\n"
        "# Example:\n"""
        "# C:\\ROMs\\n64\\My Rom File.z64\""
    )

    whitelist_cfg = Path(f'{config_folder}\\whitelist.cfg')
    whitelist_cfg_content = (
        "# Empty for now. To be implemented.\n"
    )

    config_cfg = Path(f'{config_folder}\\config.cfg')
    config_cfg_content = (
        "# Empty for now. To be implemented.\n"
    )

    readme_file = Path(f'{path}\\readme.txt')
    readme_file_content = (
        "# Rom Detective\n"
        "\n"
        "This is an INCOMPLETE version, there's no GUI here, and it probably won't run properly unless you build it manually from source.\n"
        "\n"
        "Source: https://github.com/sondregronas/Rom-Detective\n"
    )

    if not blacklist_cfg.exists():
        open(blacklist_cfg, 'w+').write(blacklist_cfg_content)
    if not whitelist_cfg.exists():
        open(whitelist_cfg, 'w+').write(whitelist_cfg_content)
    if not config_cfg.exists():
        open(config_cfg, 'w+').write(config_cfg_content)

    if not readme_file.exists():
        open(readme_file, 'w+').write(readme_file_content)

    return True
