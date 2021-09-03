import pytest

from datetime import datetime

from hltv_api.filter import HLTVFilter
from hltv_api.exceptions import HLTVInvalidInputException

def test_filter_correct_default_values():
    hltv_filter = HLTVFilter()
    assert hltv_filter.to_params() == {
            "startDate" : None,
            "endDate" : None,
            "maps" : [],
            "events" : [],
            "players" : [],
            "teams" : [],
            "stars" : None,
            "requireAllTeams" : None,
            "requireAllPlayers" : None
        } 

def test_filter_parse_dates_from_string():
    start_date = "15/01/2001"
    end_date = "15/01/2001"

    hltv_filter = HLTVFilter(start_date=start_date, end_date=end_date)
    param = hltv_filter.to_params()
    assert param["startDate"] == "15-01-2001"
    assert param["endDate"] == "15-01-2001"

def test_filter_parse_dates_from_datetime():
    start_date = datetime(year=2020, month=1, day=15) 
    end_date = datetime(year=2020, month=1, day=15)

    hltv_filter = HLTVFilter(start_date=start_date, end_date=end_date)
    param = hltv_filter.to_params()
    assert param["startDate"] == "15-01-2020"
    assert param["endDate"] == "15-01-2020"

def test_filter_invalid_maps_throw_error():
    with pytest.raises(HLTVInvalidInputException) as e:
        hltv_filter = HLTVFilter(maps=["invalid_map"])

def test_filter_valid_maps_accepted():
    maps = ["cache", "dust2"]
    hltv_filter = HLTVFilter(maps=maps)
    assert hltv_filter.to_params()["maps"] == ["de_cache", "de_dust2"]

def test_filter_invalid_stars_throw_error():
    with pytest.raises(HLTVInvalidInputException) as e:
        hltv_filter = HLTVFilter(stars=0)

def test_filter_valid_stars_accepted():
    filters = [HLTVFilter(stars=num) for num in range(1,6)]
    
    for i, hltv_filter in enumerate(filters):
        assert hltv_filter.to_params()["stars"] == i + 1 
    
