import os
import time
import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

from hltv_api.query import HLTVQuery
from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.results import get_results_matches_uris 

MATCHES_COLUMNS = ["match_id", "date", "team_1", "team_2", "team_1_id", "team_2_id", 
                    "map", "team_1_ct", "team_2_t", "team_1_t", "team_2_ct", "starting_ct"]

def get_matches_stats(skip=0, limit=None, batch_size=100, query=None, **kwargs):
    """Hits the HLTV webpage and gets the details for the matches.

    Parameter
    ---------
    skip: Optional[int]
        The number of results to be skipped from being returned. 
        If not specified, do not skip any records.

    limit: Optional[int] 
        The maximum number of results to be returned. 
        If not specified, only return 100 records. This is the default number
        of matches displayed per page on HLTV.
        If NONE, return all the records found.

    batch_size: Optional[int]
        Number of matches to be fetched in 1 iteration. This determines how frequent
        data is written into the DataFrame. If {batch_size} is 1 then data is never lost
        once it has been fetched, but slows down computation. If {batch_size == limit}
        then 1 failed request may result in an empty DataFrame.

    query: Optional[HLTVQuery]
        Query and filter for data required.

    Return
    ------
    pandas.DataFrame containing all matches found that matched the criterias.

    """
    query = query or HLTVQuery(**kwargs)
    df = pd.DataFrame(columns=MATCHES_COLUMNS)

    while (limit is None) or (len(df) < limit):  
        batch_limit = batch_size if limit is None else min(batch_size, limit - len(df))
        match_uris = get_results_matches_uris(
            skip=skip, 
            limit=batch_limit,
            query=query
        )

        # Breaks if no result found
        if len(match_uris) == 0:
            break

        # Fetches match statistics using its ID
        matches_stats = [
            stat 
            for match_uri in match_uris 
                for stat in get_match_stats_by_identifier(match_uri=match_uri)
        ]
       
        df = df.append(matches_stats) 
        skip += len(match_uris) 
            
    return df

def get_match_stats_by_identifier(match_uri=None, match_id=None):
    """Return the JSON details for the match by its match_id.

    Parameter
    ---------
    match_uri: Optional[str]
        HLTV endpoint that identifies the match. This usually has the format
        /matches/{id}/{event-name}
    match_id: Optional[Union[str, int]]
        Match identifier.

    Return
    ------
    List of dictionary objects containing the fields specified in {columns}
        
    """
    if match_uri is not None:
        match_id = match_uri.split(sep="/")[2]
    elif match_id is not None:
        # URL requires the event name but does not matter if it is 
        # not the event corresponding to the ID
        match_id = str(match_id)
        match_uri = os.path.join("/", HLTVConfig["matches_uri"], match_id, "foo") 
    else:
        raise Exception("Expecting match_uri or match_id to be not None")

    client = HLTVClient()
    match_url = urljoin(HLTVConfig["base_url"], match_uri)
    response = client.get(match_url)

    tree = html.fromstring(response.text)

    # Date
    date_obj = tree.find_class("date")[0].text_content()
    date_str = parser.parse(date_obj) 
    date = date_str.strftime(HLTVConfig["date_format"])

    # Team 1  
    team_one = tree.find_class("teamName")[0].text_content()
    team_one_uri = tree.find_class("team1-gradient")[0].xpath(".//a")[0].get("href")
    team_one_id = team_one_uri.split(sep="/")[2]

    # Team 2
    team_two = tree.find_class("teamName")[1].text_content() 
    team_two_uri = tree.find_class("team2-gradient")[0].xpath(".//a")[0].get("href")
    team_two_id = team_two_uri.split(sep="/")[2]
   
    # Maps played
    map_picks = tree.find_class("mapholder")
    maps = []

    for map_pick in map_picks:
        if len(map_pick.find_class("played")) == 0:
            continue
       
        maps.append({ 
            "match_id" : match_id,
            "date" : date, 
            "team_1" : team_one,
            "team_1_id" : team_one_id,
            "team_2" : team_two,
            "team_2_id" : team_two_id,
            **_parse_match_tree(map_pick)
        })
    return maps

def _parse_match_tree(html):
    """Parses the HTML for a 'mapholder' class.

    Parameter
    ---------
    html: the section in the HTML page for each map. This is normally 
          <div class="mapholder"> ... </div>
    
    Return
    ------
    Dictionary object with the specified fields 
    """
    # Name of current map
    map_name = html.find_class("mapname")[0].text_content()

    # Scores for CT and T sides for each half
    ct_scores = [score.text_content() for score in html.find_class("ct")]
    t_scores = [score.text_content() for score in html.find_class("t")]

    # Team 1 starts on CT or T side
    team_1_starting = html.find_class("results-center-half-score")[0].xpath(".//span")[1].get("class")

    # 1 iff team_1 starts on CT, 2 otherwise (team_2 starts on CT)
    if team_1_starting == "ct":
        starting_ct = 1

        team_1_ct = ct_scores[0]
        team_1_t = t_scores[1]

        team_2_ct = ct_scores[1]
        team_2_t = t_scores[0]
    else:
        starting_ct = 2

        team_1_ct = ct_scores[1]
        team_1_t = t_scores[0]

        team_2_ct = ct_scores[0]
        team_2_t = t_scores[1]

    return { 
        "map" : map_name.lower(),
        "team_1_t" : int(team_1_t),
        "team_1_ct" : int(team_1_ct),
        "team_2_t" : int(team_2_t),
        "team_2_ct" : int(team_2_ct),
        "starting_ct" : starting_ct
    }
