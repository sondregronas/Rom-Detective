import pytest

from rom_detective.class_indexer_platform import Platform, import_platforms_yaml, identify_platform, identify_platform_by_id
from test_const import TEST_FILES_PATH


def test_platform_import_yaml():
    platforms = import_platforms_yaml(f'{TEST_FILES_PATH}\\platforms.yaml')
    test = Platform(id='test1', name='Test Number 1', aliases=['test 1', 'test 2'], extensions=['.test1'])

    assert test in platforms


def test_platform_str():
    test = Platform(id='test', name='test', aliases=['test'], extensions=['.test'])
    assert str(test) == """Platform: test (test). Aliases=['test']"""


def test_identify_platform():
    """Test identification of platforms"""
    win = Platform(id='win', name='Windows 10', aliases=['win10'], extensions=[''])
    xbox = Platform(id='xbox360', name='Microsoft Xbox 360', aliases=['xbox'], extensions=[''])

    platforms = [win, xbox]

    # Ensure first parent is identified
    assert identify_platform(r'C:\Windows\ROMs\xbox360', platforms=platforms) == xbox
    assert identify_platform(r'C:\Windows\ROMs\xbox360\Windows 10', platforms=platforms) == win

    # Ensure Alias works to identify
    assert identify_platform('Microsoft Xbox 360', platforms=platforms) == xbox

    # Ensure identify_platform_by_id works
    assert identify_platform_by_id('xbox360', platforms=platforms) == xbox

    # Ensure non-identified platforms raise a warning
    with pytest.raises(Warning):
        identify_platform(r'C:\test\folder', platforms=platforms)
    with pytest.raises(Warning):
        identify_platform_by_id('test', platforms=platforms)
