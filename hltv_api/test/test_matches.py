from hltv_api.query import HLTVQuery 
from hltv_api.matches import get_matches_stats, get_match_stats_by_identifier

def test_matches_stats_limit_zero():
    df = get_matches_stats(limit=0)
    assert len(df) == 0

def test_matches_stats_limit_one():
    df = get_matches_stats(limit=1)
    assert len(df) == 1

def test_matches_stats_simple_query():
    query = HLTVQuery(start_date="1st Sep 2021", end_date="2nd Sep 2021")
    df = get_matches_stats(limit=1, query=query)
    import pandas as pd
    pd.set_option('display.max_columns', None)
    print(df.head(3))

    # 3 maps played in this game
    assert len(df) == 3

    # 2nd map
    game = df.iloc[1, :].to_dict()
    assert game == {
       "match_id" : "2350368",
       "date" : "2021-09-02",
       "team_1" : "Gambit",
       "team_2" : "Liquid",
       "team_1_id" : "6651",
       "team_2_id" : "5973",
       "map" : "vertigo",
       "team_1_ct" : 9,
       "team_2_t" : 6,
       "team_1_t" : 6,
       "team_2_ct" : 9,
       "starting_ct" : 2
    }

def test_match_stats_by_match_id():
    stats = get_match_stats_by_identifier(match_id=2350368)

    # 3 maps played in this game
    assert len(stats) == 3

    # 3rd map
    assert stats[2] == {
       "match_id" : "2350368",
       "date" : "2021-09-02",
       "team_1" : "Gambit",
       "team_2" : "Liquid",
       "team_1_id" : "6651",
       "team_2_id" : "5973",
       "map" : "mirage",
       "team_1_ct" : 10,
       "team_2_t" : 3,
       "team_1_t" : 6,
       "team_2_ct" : 9,
       "starting_ct" : 2
    }

def test_match_stats_by_match_uri():
    uri = "/matches/2350368/gambit-vs-liquid-esl-pro-league-season-14"
    stats = get_match_stats_by_identifier(match_uri=uri)

    # 3 maps played in this game
    assert len(stats) == 3

    # 1st map
    assert stats[0] == {
       "match_id" : "2350368",
       "date" : "2021-09-02",
       "team_1" : "Gambit",
       "team_2" : "Liquid",
       "team_1_id" : "6651",
       "team_2_id" : "5973",
       "map" : "inferno",
       "team_1_ct" : 6,
       "team_2_t" : 9,
       "team_1_t" : 6,
       "team_2_ct" : 7,
       "starting_ct" : 1
    }
