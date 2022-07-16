from rom_detective._const_ import DATA_FOLDER
from rom_detective.class_indexer_platform import import_platforms_yaml
from rom_detective.class_databases import DatabaseFiles

PLATFORMS_RAW = import_platforms_yaml(f'{DATA_FOLDER}\\platforms.yaml')
PLATFORMS = {platform.id: platform for platform in PLATFORMS_RAW}

DATABASES = DatabaseFiles()
