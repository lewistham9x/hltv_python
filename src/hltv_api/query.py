from datetime import datetime
from typing import Union, Optional, List

from dateutil import parser

from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.exceptions import HLTVInvalidInputException


class HLTVQuery():
    """Hits the HLTV webpage and gets the details for the matches.

    Attribute 
    ---------
    match_type: Optional[str]
        LAN or Online games.

    start_date: Optional[Union[str, datetime]]
        Date of the first result with the format '%d-%m-%Y'

    end_date: Optional[Union[str, datetime]]
        Date of the last result with the format '%d-%m-%Y'

    maps: Optional[List[str]]
        Only matches that include these maps will be returned.
        Available maps include all maps that have been in the official map pool.

    events: Optional[List[Union[str, int]]]
        List of event ids to choose from.

    teams: Optional[List[Union[str, int]]]
        List of team ids to choose from.
        
    players: Optional[List[Union[str, int]]]
        List of players ids to choose from.
    
    stars: Optional[int]
        Only choose games with specified HLTV star rating. If not specified,
        return all matches found.

    require_all_teams: Optional[bool]
        Only return matches where both teams are in `teams`.

    require_all_players: Optional[bool]
        Only return matches where all `players` are in the line-up.

    """
    MATCH_TYPES = frozenset(["lan, online"])
    STARS = range(1, 6)
    MAPS = frozenset(["cache", "season", "dust2", "mirage", "inferno", "nuke",
                      "train", "cobblestone", "overpass", "tuscan",
                      "vertigo", "ancient"])

    def __init__(
            self,
            match_type: Optional[str] = None,
            start_date: Optional[Union[str, datetime]] = None,
            end_date: Optional[Union[str, datetime]] = None,
            maps: Optional[List[str]] = [],
            event_ids: Optional[List[Union[int, str]]] = [],
            event_names: Optional[List[str]] = [],
            player_ids: Optional[List[Union[int, str]]] = [],
            player_names: Optional[List[str]] = [],
            team_ids: Optional[List[Union[int, str]]] = [],
            team_names: Optional[List[str]] = [],
            stars: Optional[int] = None,
            require_all_teams: Optional[bool] = None,
            require_all_players: Optional[bool] = None
    ):
        # Validate match_type
        if match_type is not None and match_type.lower() not in HLTVQuery.MATCH_TYPES:
            raise HLTVInvalidInputException(
                message=f"Invalid match_type: {match_type}",
                expected=f"One of {HLTVQuery.MATCH_TYPES}",
            )
        self.match_type = match_type

        # Validate dates
        if start_date is None:
            self.start_date = None
        elif type(start_date) == str:
            self.start_date = parser.parse(start_date).strftime(HLTVConfig["date_format"])
        else:
            self.start_date = start_date.strftime(HLTVConfig["date_format"])

        if end_date is None:
            self.end_date = None
        elif type(end_date) == str:
            self.end_date = parser.parse(end_date).strftime(HLTVConfig["date_format"])
        else:
            self.end_date = end_date.strftime(HLTVConfig["date_format"])

        # Validate maps
        if all(elem in HLTVQuery.MAPS for elem in maps):
            self.maps = [f"de_{mapname}" for mapname in maps]
        else:
            raise HLTVInvalidInputException(
                message=f"1 or more invalid map name in {maps}",
                expected="One of {HLTVQuery.MAPS}"
            )

        # Event IDs
        self.event_ids = [int(e) for e in event_ids]
        self.event_names = event_names

        # Player IDs
        self.player_ids = [int(p) for p in player_ids]
        self.player_names = player_names

        # Team IDs
        self.team_ids = [int(t) for t in team_ids]
        self.team_names = team_names

        # Validate number of stars for the game
        if stars is None or stars in range(1, 6):
            self.stars = stars
        else:
            raise HLTVInvalidInputException(
                message=f"Stars can only be between 1 and 5",
                expected="Integer between 1 and 5 inclusive"
            )

        # HLTV considers this as a flag so the 'truth-value' does not matter
        # Hence making it 'None' removes it from the query parameter
        self.require_all_teams = require_all_teams or None
        self.require_all_players = require_all_players or None

    def _aggregate_events(self):
        client = HLTVClient()
        event_ids_from_names = [matching_event["id"]
                                for event_name in self.event_names
                                for matching_event in client.search_event(event_name)]
        return list(dict.fromkeys([*self.event_ids, *event_ids_from_names]))

    def _aggregate_players(self):
        client = HLTVClient()
        player_ids_from_names = [matching_player["id"]
                                 for player_name in self.player_names
                                 for matching_player in client.search_player(player_name)]
        return list(dict.fromkeys([*self.player_ids, *player_ids_from_names]))

    def _aggregate_teams(self):
        client = HLTVClient()
        team_ids_from_names = [matching_team["id"]
                               for team_name in self.team_names
                               for matching_team in client.search_team(team_name)]
        return list(dict.fromkeys([*self.team_ids, *team_ids_from_names]))

    def to_params(self):
        return {
            "startDate": self.start_date,
            "endDate": self.end_date,
            "map": self.maps,
            "event": self._aggregate_events(),
            "player": self._aggregate_players(),
            "team": self._aggregate_teams(),
            "stars": self.stars,
            "requireAllTeams": self.require_all_teams,
            "requireAllPlayers": self.require_all_players
        }
