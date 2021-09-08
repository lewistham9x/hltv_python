import os
from urllib.parse import urljoin

import pandas as pd
from dateutil import parser
from lxml import html

from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.query import HLTVQuery
from hltv_api.results import get_past_matches_ids

MATCHES_COLUMNS = ["match_id", "date", "team_1", "team_2", "team_1_id", "team_2_id",
                   "map", "team_1_ct", "team_2_t", "team_1_t", "team_2_ct", "starting_ct"]

ROUND_STATS_COLUMNS = [[f"{i}_team_1_value", f"{i}_team_2_value", f"{i}_winner"]
                       for i in range(1, 31)]


def get_matches_stats(skip=0, limit=None, batch_size=100, query=None, include_round_economy=False, **kwargs):
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

    include_round_stats: Optional[bool]
        If `True`, data return will contains details on the round statistics such as
        economy (total equipment values, pistol?, etc...),
        round history (defusal, kills, bomb explosion, etc...).

        Note that to get this information, an extra GET request is made for each match.

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
        matches_ids = get_past_matches_ids(
            skip=skip,
            limit=batch_limit,
            query=query
        )

        # Breaks if no result found
        if len(matches_ids) == 0:
            break

        # Fetches match statistics using its ID
        matches_stats = [
            stat
            for match_id in matches_ids
            for stat in get_match_stats_by_id(match_id)
        ]

        df = df.append(matches_stats)
        skip += len(matches_ids)

    return df


def get_match_stats_by_id(match_id):
    """Return the JSON details for the match by its match_id.

    Parameter
    ---------
    match_id: Optional[Union[str, int]]
        Match identifier.

    Return
    ------
    List of dictionary objects containing the fields specified in {columns}
        
    """

    # URL requires the event name but does not matter if it is
    # not the event corresponding to the ID
    match_id = str(match_id)
    match_uri = os.path.join("/", HLTVConfig["matches_uri"], match_id, "foo")

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
            "match_id": match_id,
            "date": date,
            "team_1": team_one,
            "team_1_id": team_one_id,
            "team_2": team_two,
            "team_2_id": team_two_id,
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
        "map": map_name.lower(),
        "team_1_t": int(team_1_t),
        "team_1_ct": int(team_1_ct),
        "team_2_t": int(team_2_t),
        "team_2_ct": int(team_2_ct),
        "starting_ct": starting_ct
    }


def get_rounds_summary_by_match_id(match_id):
    # URL requires the event name but does not matter if it is
    # not the event corresponding to the ID
    match_id = str(match_id)
    uri = os.path.join("/", HLTVConfig["economy_uri"], match_id, "foo")

    client = HLTVClient()
    match_url = urljoin(HLTVConfig["base_url"], uri)
    response = client.get(match_url)

    tree = html.fromstring(response.text)

    history = [half.find_class("equipment-category-td")
               for half in tree.find_class("team-categories")]

    team_1_rounds = [*history[0], *history[2]]
    team_2_rounds = [*history[1], *history[3]]

    results = {}
    for i in range(0, 30):
        team_1_value = team_2_value = winner = None
        if i < len(team_1_rounds):
            team_1_value = team_1_rounds[i].get("title").strip("Equipment value: ")
            team_2_value = team_2_rounds[i].get("title").strip("Equipment value: ")

            winner = 1 if len(team_2_rounds[i].find_class("lost")) > 0 else 2

        results[f"{i + 1}_team_1_value"] = int(team_1_value)
        results[f"{i + 1}_team_2_value"] = int(team_2_value)
        results[f"{i + 1}_winner"] = int(winner)

    return results
