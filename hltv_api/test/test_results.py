from hltv_api.query import HLTVQuery 
from hltv_api.results import HLTVResults

def test_empty_dataframe_when_limit_is_zero():
    df = HLTVResults().get_results(limit=0)
    assert len(df) == 0

def test_single_result_when_limit_is_one():
    df = HLTVResults().get_results(limit=1)
    assert len(df) == 1

def test_get_result_with_simple_query():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    df = HLTVResults().get_results(limit=1, query=query)

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

