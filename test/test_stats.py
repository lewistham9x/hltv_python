from hltv_api.api.stats import get_economy_by_match_id, get_matches_with_economy


def test_matches_stats_limit_zero():
    df = get_matches_with_economy(limit=0)
    assert len(df) == 0


def test_matches_stats_limit_one():
    df = get_matches_with_economy(limit=1)
    assert len(set(df["match_id"])) == 1


def test_matches_no_limit_zero_result():
    df = get_matches_with_economy(team_names=["FaZe", "OG"], player_names=["s1mple"],
                                  require_all_teams=True)
    assert len(df) == 0


def test_matches_stats_simple_query():
    df = get_matches_with_economy(limit=1, start_date="1st Sep 2021", end_date="2nd Sep 2021")

    # 3 maps played in this game
    # assert len(df) == 3

    # 2nd map
    game = df.iloc[1, :].to_dict()

    assert game["map"] == "vertigo"


def test_get_economy_by_match_id():
    res = get_economy_by_match_id(2350360)

    # Correct number of maps
    assert len(res["maps"]) == 2

    # First map is inferno
    inferno = res["maps"][0]
    assert inferno["map"] == "inferno"

    assert inferno["1_team_1_value"] == 4400
    assert inferno["1_team_2_value"] == 4000
    assert inferno["1_winner"] == 2

    # This game has 23 rounds
    assert inferno["24_team_1_value"] is None
    assert inferno["24_team_2_value"] is None
    assert inferno["24_winner"] is None
