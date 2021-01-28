import pytest

from usb.utils import parse_season, parse_episodes, move_id


@pytest.fixture
def episode_multi():
    return "s05e17e18"


@pytest.fixture
def episode_single():
    return "S07E09"


@pytest.fixture
def document_id():
    return "seinfeld-5-7-345"


@pytest.fixture
def double_ep_id():
    return "seinfeld-9-23-24-1200"


@pytest.fixture
def invalid_id():
    return "seinfeld-5-345"


def test_parse_season(episode_single, episode_multi):
    assert parse_season(episode_single)
    assert parse_season(episode_single) == 7
    assert parse_season(episode_multi) == 5


def test_parse_episodes(episode_single, episode_multi):
    assert parse_episodes(episode_single)
    assert set(parse_episodes(episode_single)) == {9}
    assert set(parse_episodes(episode_multi)) == {17, 18}


def test_increment_id(document_id):
    assert move_id(document_id, 1) == "seinfeld-5-7-346"
    assert move_id(document_id, 5) == "seinfeld-5-7-350"


def test_decrement_id(document_id):
    assert move_id(document_id, -1) == "seinfeld-5-7-344"
    assert move_id(document_id, -11) == "seinfeld-5-7-334"
