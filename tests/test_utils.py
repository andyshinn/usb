import pytest

from usb.utils import parse_season, parse_episodes


@pytest.fixture
def episode_multi():
    return 's05e17e18'


@pytest.fixture
def episode_single():
    return 'S07E09'


def test_parse_season(episode_single, episode_multi):
    assert parse_season(episode_single)
    assert parse_season(episode_single) is 7
    assert parse_season(episode_multi) is 5


def test_parse_episodes(episode_single, episode_multi):
    assert parse_episodes(episode_single)
    assert set(parse_episodes(episode_single)) == set([9])
    assert set(parse_episodes(episode_multi)) == set([17,18])
