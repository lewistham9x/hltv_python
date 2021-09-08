HLTVConfig = {
    "base_url": "https://www.hltv.org",

    "matches_uri": "matches",
    "results_uri": "results",
    "teams_uri": "teams",
    "players_uri": "players",
    "stats_uri": "stats",

    "economy_uri": "stats/matches/mapstatsid",

    "search_teams_uri": "searchTeam",
    "search_players_uri": "searchPlayer",
    "search_events_uri": "searchEvent",

    "date_format": "%Y-%m-%d"
}


def basic_hltv_config(key, value):
    global HLTVConfig

    if key not in HLTVConfig:
        raise KeyError(f"{key} is not a valid field in HLTV config")

    HLTVConfig[key] = value
