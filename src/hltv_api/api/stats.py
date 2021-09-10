import os
from urllib.parse import urljoin

import pandas as pd
from lxml import html

from hltv_api.api.results import get_past_matches_ids
from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.pages.matches import parse_match_page
from hltv_api.pages.stats import parse_map_stat_economy_page
from hltv_api.query import HLTVQuery

MATCH_COLUMNS = ["match_id", "map", "team_1_id", "team_2_id", "starting_ct"]
ROUNDS_COLUMNS = [col
                  for i in range(1, 31)
                  for col in [f"{i}_team_1_value", f"{i}_team_2_value", f"{i}_winner"]]


def get_matches_with_economy(skip=0, limit=None, batch_size=100, query=None, **kwargs):
    """Return a DataFrame containing

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

    query: Optional[HLTVQuery]
        Queries and filters for the data.

    kwargs:
        Arguments to `HLTVQuery` if `query` is `None`.

    """
    query = query or HLTVQuery(**kwargs)

    columns = MATCH_COLUMNS + ROUNDS_COLUMNS
    df = pd.DataFrame(columns=columns)

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
        matches_stats = []
        for match_id in matches_ids:
            stats = get_economy_by_match_id(match_id)
            for map_details in stats["maps"]:
                pivoted = {**map_details, **stats}
                matches_stats.append({k: v for k, v in pivoted.items() if k in columns})

        df = df.append(matches_stats)
        skip += len(matches_ids)

    return df


def get_economy_by_match_id(match_id):
    client = HLTVClient()

    # URL requires the event name but does not matter if it is
    # not the event corresponding to the ID
    match_id = str(match_id)
    match_uri = os.path.join(HLTVConfig["matches_uri"], match_id, "foo")
    match_url = urljoin(HLTVConfig["base_url"], match_uri)
    response = client.get(match_url)

    match_page = html.fromstring(response.text)
    match_details = parse_match_page(match_page)

    match_details["maps"] = [{
        **map_played,
        **get_economy_by_map_stats_id(map_played["map_stats_id"])
    } for map_played in match_details["maps"]]

    return match_details


def get_economy_by_map_stats_id(map_stats_id):
    client = HLTVClient()

    map_stats_uri = os.path.join(HLTVConfig["economy_uri"], str(map_stats_id), "foo")
    map_stats_url = urljoin(HLTVConfig["base_url"], map_stats_uri)
    map_stat_response = client.get(map_stats_url)

    tree = html.fromstring(map_stat_response.text)
    return parse_map_stat_economy_page(tree)
