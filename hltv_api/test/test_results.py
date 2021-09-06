from hltv_api.query import HLTVQuery 
from hltv_api.results import get_results, get_results_matches_uris 

def test_get_result_empty_dataframe_when_limit_is_zero():
    df = get_results(limit=0)
    assert len(df) == 0

def test_get_result_single_result_when_limit_is_one():
    df = get_results(limit=1)
    assert len(df) == 1

def test_get_result_with_simple_query():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    df = get_results(limit=1, query=query)

    res = df.iloc[0, :].to_dict()
    assert res == {
       "match_id" : "2350368",
       "date" : "2021-09-02",
       "event" : "ESL Pro League Season 14",
       "team_1" : "Gambit",
       "team_2" : "Liquid",
       "map" : "bo3",
       "score_1" : 2,
       "score_2" : 1,
       "stars" : 2
    }

def test_get_result_complex_filter():
    query = HLTVQuery(start_date="1st Sep 2020", end_date="1st Sep 2021",
                      teams=[4608, 6651], require_all_teams=True)
    df = get_results(limit=3, query=query)

    # Expect exactly 3 results
    assert len(df) == 3

    # Comparing 2nd result 
    game = df.iloc[1, :].to_dict()
    assert game == {
       "match_id" : "2349630",
       "date" : "2021-07-03",
       "event" : "StarLadder CIS RMR 2021",
       "team_1" : "Gambit",
       "team_2" : "Natus Vincere",
       "map" : "bo3",
       "score_1" : 2,
       "score_2" : 1,
       "stars" : 5
    }
    
def test_get_matches_uri_work_for_single_result():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    uris = get_results_matches_uris(limit=1, query=query)

    assert len(uris) == 1
    assert uris[0] == "/matches/2350368/gambit-vs-liquid-esl-pro-league-season-14"

def test_get_matches_uri_work_for_multiple_results():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    uris = get_results_matches_uris(limit=3, query=query)

    assert len(uris) == 3
    assert uris == [
        "/matches/2350368/gambit-vs-liquid-esl-pro-league-season-14",
        "/matches/2351027/copenhagen-flames-vs-opaa-iem-fall-2021-europe-open-qualifier-2",
        "/matches/2351022/honoris-vs-cowana-iem-fall-2021-europe-open-qualifier-2"
    ]

