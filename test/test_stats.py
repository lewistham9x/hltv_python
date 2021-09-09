from hltv_api.api.stats import get_economy_by_match_id


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

