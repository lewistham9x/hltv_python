from dateutil import parser
from datetime import datetime
from typing import Union, Optional, List

from hltv_api.exceptions import HLTVInvalidInputException

class HLTVFilter():
    MATCH_TYPES = frozenset(["lan, online"])
    STARS = range(1,6)
    MAPS = frozenset(["cache", "season", "dust2", "mirage", "inferno", "nuke", 
                      "train", "cobblestone", "overpass", "tuscan", 
                      "vertigo", "ancient"])
    DATE_FORMAT = "%d-%m-%Y"

    def __init__(
        self, 
        match_type: Optional[str] = None, 
        start_date: Optional[Union[str, datetime]] = None, 
        end_date: Optional[Union[str, datetime]] = None, 
        maps: Optional[List[str]] = [], 
        events: Optional[List[int]] = [], 
        players: Optional[List[int]] = [], 
        teams: Optional[List[int]] = [], 
        stars: Optional[int] = None,
        require_all_teams: Optional[bool] = None,
        require_all_players: Optional[bool] = None
    ):
        # Validate match_type
        if match_type is not None and match_type.lower() not in HLTVFilter.MATCH_TYPES:
            raise HLTVInvalidInputException(
                message=f"Invalid match_type: {match_type}",
                expected=f"One of {HLTVFilter.MATCH_TYPES}",
            )
        self.match_type = match_type

        # Validate dates
        if start_date is None:
            self.start_date = None
        elif type(start_date) == str:
            self.start_date = parser.parse(start_date).strftime(HLTVFilter.DATE_FORMAT)
        else:
            self.start_date = start_date.strftime(HLTVFilter.DATE_FORMAT)
        
        if end_date is None:
            self.end_date = None
        elif type(end_date) == str:
            self.end_date = parser.parse(end_date).strftime(HLTVFilter.DATE_FORMAT)
        else:
            self.end_date = end_date.strftime(HLTVFilter.DATE_FORMAT)

        # Validate maps
        if all(elem in HLTVFilter.MAPS for elem in maps):
            self.maps = [f"de_{mapname}" for mapname in maps]
        else:
            raise HLTVInvalidInputException(
                message=f"1 or more invalid map name in {maps}",
                expected="One of {HLTVFilter.MAPS}"
            )

        # Event IDs
        self.events=events

        # Player IDs
        self.players=players

        # Team IDs
        self.teams=teams

        # Validate number of stars for the game
        if stars is None or stars in range(1,6):
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
    
    def to_params(self):
        return {
            "startDate" : self.start_date,
            "endDate" : self.end_date,
            "maps" : self.maps,
            "events" : self.events,
            "players" : self.players,
            "teams" : self.teams,
            "stars" : self.stars,
            "requireAllTeams" : self.require_all_teams,
            "requireAllPlayers" : self.require_all_players
        }
