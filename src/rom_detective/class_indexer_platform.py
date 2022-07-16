import yaml

from dataclasses import dataclass


@dataclass
class Platform:
    """
    id: 'n64', 'win'
    name: 'Nintendo 64', 'Windows'
    aliases: ['nintendo64', +'nintendo 64', +'n64'],
             ['win10','win11','windows10','windows11', +'windows', +'win']
    """
    id: str
    name: str
    aliases: list[str]
    extensions: list[str]

    def __str__(self) -> str:
        return f'Platform: {self.name} ({self.id}). Aliases={self.aliases}'

    def __post_init__(self) -> None:
        """Add name and id to aliases"""
        self.aliases += [self.name.lower()]
        self.aliases += [self.id.lower()]
        # Remove duplicate entries from aliases
        self.aliases = list(dict.fromkeys(self.aliases))

    def matches_alias(self, alias) -> bool:
        """Boolean check if an alias matches that of the platform aliases"""
        return True if alias in self.aliases else False


def import_platforms_yaml(yaml_file: str) -> list[Platform]:
    with open(yaml_file) as file:
        return [Platform(id=v['id'],
                         name=k,
                         aliases=v['aliases'],
                         extensions=v['extensions'])
                for k, v in yaml.full_load(file).items()]


def identify_platform(path_or_alias: str, platforms: list[Platform]) -> Platform:
    """
    Takes a str of a path or alias (and optionally a list of Platforms) to a ROM and returns
    a corresponding platform if a parent folder matches one of the platform aliases.

    List goes from child to parent meaning 'C:\\Windows\\ROMs\\xbox360'
    would return a platform object for xbox360, not Windows

    Raises a warning if no platform is identified
    """
    for folder in reversed(path_or_alias.lower().split('\\')):
        output = [x for x in platforms if x.matches_alias(folder)]
        if output:
            return output[0]
    raise Warning(f"Could not find a platform for {path_or_alias}")


def identify_platform_by_id(platform_id: str, platforms: list[Platform]) -> Platform:
    """
    Takes a str of a platform id (and optionally a list of Platforms)
    and returns the corresponding platform, if it matches

    Raises a warning if no platform is identified
    """
    output = [x for x in platforms if x.id == platform_id]
    if not output:
        raise Warning(f"Could not find a platform for {platform_id}")
    return output[0]
