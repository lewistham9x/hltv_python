from datetime import datetime

from hltv_api.api.results import get_past_matches_ids, get_results
from hltv_api.query import HLTVQuery


def test_get_result_empty_dataframe_when_limit_is_zero():
    df = get_results(limit=0)
    assert len(df) == 0


def test_get_result_single_result_when_limit_is_one():
    df = get_results(limit=1)
    assert len(df) == 1


def test_get_result_filter_no_result():
    df = get_results(team_names=["Faze", "OG"], player_names=["s1mple"], require_all_teams=True)
    assert len(df) == 0


def test_get_result_no_limit():
    df = get_results(team_names=["Faze", "OG"], player_names=["s1mple"],
                     start_date=datetime(year=2021, month=6, day=1),
                     end_date=datetime(year=2021, month=9, day=1),
                     require_all_teams=True)
    assert len(df) == 0


def test_get_result_with_simple_query():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    df = get_results(limit=1, query=query)

    res = df.iloc[0, :].to_dict()
    assert res == {
        "match_id": "2350368",
        "date": "2021-09-02",
        "event": "ESL Pro League Season 14",
        "team_1": "Gambit",
        "team_2": "Liquid",
        "map": "bo3",
        "score_1": 2,
        "score_2": 1,
        "stars": 2
    }


def test_get_result_complex_filter():
    query = HLTVQuery(start_date="1st Sep 2020", end_date="1st Sep 2021",
                      team_ids=[4608, 6651], require_all_teams=True)
    df = get_results(limit=3, query=query)

    # Expect exactly 3 results
    assert len(df) == 3

    # Comparing 2nd result 
    game = df.iloc[1, :].to_dict()
    assert game == {
        "match_id": "2349630",
        "date": "2021-07-03",
        "event": "StarLadder CIS RMR 2021",
        "team_1": "Gambit",
        "team_2": "Natus Vincere",
        "map": "bo3",
        "score_1": 2,
        "score_2": 1,
        "stars": 5
    }


def test_get_past_matches_ids_work_for_single_result():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    ids = get_past_matches_ids(limit=1, query=query)

    assert len(ids) == 1
    assert ids[0] == "2350368"


def test_get_past_matches_ids_work_for_multiple_results():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    ids = get_past_matches_ids(limit=3, query=query)

    assert len(ids) == 3
    assert ids == ["2350368", "2351027", "2351022"]


def test_get_past_matches_ids_work_for_no_results():
    ids = get_past_matches_ids(team_names=["Faze", "OG"], player_names=["s1mple"], require_all_teams=True)

    assert len(ids) == 0
