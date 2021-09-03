HLTVConfig = {
    "base_url" : "https://www.hltv.org",
    "matches_uri" : "matches",
    "results_uri" : "results",
    "teams_uri" : "teams",
    "players_uri" : "players",
    "search_teams_uri" : "searchTeam",
    "search_players_uri" : "searchPlayer"
}

MAPS = frozenset(["cache", "season", "dust2", "mirage", "inferno", "nuke", 
                  "train", "cobblestone", "overpass", "tuscan", 
                  "vertigo", "ancient"])


def basic_hltv_config(key, value):
    global HLTVConfig

    if key not in HLTVConfig:
        raise KeyError(f"{key} is not a valid field in HLTV config")

    HLTVConfig[key] = value

