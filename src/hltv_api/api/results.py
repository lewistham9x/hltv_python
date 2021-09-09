from urllib.parse import urljoin

import pandas as pd
from lxml import html

from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.pages.results import RESULTS_COLUMNS, parse_result_page
from hltv_api.query import HLTVQuery


def get_results(skip=0, limit=None, query=None, **kwargs):
    """Fetches data for the results filtered by `query`.

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
        Query and filter for data required.

    kwargs:
        Arguments to pass to HLTVQuery if `query` is `None`.

    Return
    ------
    pandas.DataFrame
    """

    query = query or HLTVQuery(**kwargs)
    url = urljoin(HLTVConfig["base_url"], HLTVConfig["results_uri"])

    df = pd.DataFrame(columns=RESULTS_COLUMNS)

    client = HLTVClient()
    while (limit is None) or (len(df) < limit):
        response = client.get(url, params={
            "offset": skip, **query.to_params()
        })
        tree = html.fromstring(response.text)

        results = parse_result_page(tree)
        if len(results) == 0:
            break

        batch_limit = len(results) if limit is None else min(len(results), limit - len(df))

        df = df.append(results[:batch_limit])

        skip += len(df)

    return df


def get_past_matches_ids(skip=0, limit=100, query=None, **kwargs):
    """Return the IDs of matches in /results page.

    First, hits HLTV page /results?offset={skip}&startDate={start_date}&endDate={end_date}.
    Parses the HTML and gets the required number of matches, and extracts their IDs and hrefs. The hrefs contain the resource URI for the individual matches.

    The return values are these URIs which have the format:
        /matches/{id}/{match-name}

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
    results_url = urljoin(HLTVConfig["base_url"], HLTVConfig["results_uri"])
    client = HLTVClient()

    # Accumulator for all match ids
    all_matches_ids = []

    query = query or HLTVQuery(**kwargs)

    while (limit is None) or (len(all_matches_ids) < limit):
        response = client.get(results_url, params={
            "offset": skip, **query.to_params()
        })

        tree = html.fromstring(response.text)

        results = parse_result_page(tree)

        # No more results
        if len(results) == 0:
            break

        # Set the offset for the next request
        skip += len(results)

        # Adds to the accumulator
        all_matches_ids += [result["match_id"] for result in results]

    return all_matches_ids[:limit]