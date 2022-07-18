from rom_detective import DATA_FOLDER
from rom_detective.platforms import import_platforms
from rom_detective.databases import DatabaseFiles

PLATFORMS = {platform.id: platform for platform in import_platforms(f'{DATA_FOLDER}\\platforms.yaml')}
DATABASES = DatabaseFiles()
