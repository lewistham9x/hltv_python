import pytest

from datetime import datetime

from hltv_api.query import HLTVQuery
from hltv_api.exceptions import HLTVInvalidInputException

def test_query_correct_default_values():
    hltv_query = HLTVQuery()
    assert hltv_query.to_params() == {
            "startDate" : None,
            "endDate" : None,
            "map" : [],
            "event" : [],
            "player" : [],
            "team" : [],
            "stars" : None,
            "requireAllTeams" : None,
            "requireAllPlayers" : None
        } 

def test_query_parse_dates_from_string():
    start_date = "15/01/2001"
    end_date = "15/01/2001"

    hltv_query = HLTVQuery(start_date=start_date, end_date=end_date)
    param = hltv_query.to_params()
    assert param["startDate"] == "2001-01-15"
    assert param["endDate"] == "2001-01-15"

def test_query_parse_dates_from_datetime():
    start_date = datetime(year=2020, month=1, day=15) 
    end_date = datetime(year=2020, month=1, day=15)

    hltv_query = HLTVQuery(start_date=start_date, end_date=end_date)
    param = hltv_query.to_params()
    assert param["startDate"] == "2020-01-15"
    assert param["endDate"] == "2020-01-15"

def test_query_invalid_maps_throw_error():
    with pytest.raises(HLTVInvalidInputException) as e:
        hltv_query = HLTVQuery(maps=["invalid_map"])

def test_query_valid_maps_accepted():
    maps = ["cache", "dust2"]
    hltv_query = HLTVQuery(maps=maps)
    assert hltv_query.to_params()["map"] == ["de_cache", "de_dust2"]

def test_query_invalid_stars_throw_error():
    with pytest.raises(HLTVInvalidInputException) as e:
        hltv_query = HLTVQuery(stars=0)

def test_query_valid_stars_accepted():
    queries = [HLTVQuery(stars=num) for num in range(1,6)]
    
    for i, hltv_query in enumerate(queries):
        assert hltv_query.to_params()["stars"] == i + 1 
    
def test_query_team_names():
    # There are 4 teams which should match the name 'navi'
    query = HLTVQuery(team_ids=[6667], team_names=["navi"])

    team_ids = query.to_params()["team"]

    assert sorted(team_ids) == [178, 6667, 10371, 10730, 10918]

def test_query_player_names():
    # There are 4 teams which should match the name 'navi'
    query = HLTVQuery(player_ids=[3741], player_names=["s1mple", "niko"])

    player_ids = query.to_params()["player"]

    assert sorted(player_ids) == [154, 1142, 3741, 7418, 7998, 10112, 10264, 10504, 13064, 17726]

def test_query_event_names():
    # There are 4 teams which should match the name 'navi'
    query = HLTVQuery(event_ids=[2062], event_names=["ESL"])

    event_ids = query.to_params()["event"]

    assert sorted(event_ids) == [1444, 1611, 1666, 2062]
    