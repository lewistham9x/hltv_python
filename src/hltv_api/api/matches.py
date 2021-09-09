import os
from urllib.parse import urljoin

import pandas as pd
from lxml import html

from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.pages.matches import parse_match_page
from hltv_api.api.results import get_past_matches_ids
from hltv_api.query import HLTVQuery

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

    columns = MATCHES_COLUMNS
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
            stat = get_match_stats_by_id(match_id)
            for map_details in stat["maps"]:
                pivoted = {**map_details, **{k: v for k, v in stat.items()}}
                matches_stats.append({k: v for k, v in pivoted.items() if k in columns})

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

    # HTMLElement
    tree = html.fromstring(response.text)

    return parse_match_page(tree)
