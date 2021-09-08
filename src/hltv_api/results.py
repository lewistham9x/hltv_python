import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

from hltv_api.query import HLTVQuery
from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig

RESULTS_COLUMNS = ["match_id", "date", "event", "team_1", "team_2", "map", "score_1", "score_2", "stars"]

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
        response = client.get(url, params=query.to_params())
        tree = html.fromstring(response.text)

        results = _parse_result_page(tree)
        batch_limit = limit - len(df)
        df = df.append(results[:batch_limit])

        skip += len(df)

    return df

def _parse_result_page(html):
    """Parse and extract results from a `/results` page"""
    # Each result sublist contains all matches for that particular day
    results_sublist = html.find_class("allres")[0].find_class("results-sublist")
   
    all_matches = []
    # Iterate over the sublists and then individual matches
    for sublist in results_sublist:
        datetime_obj = sublist.find_class("standard-headline")[0].text_content()
        datetime_str = datetime_obj.replace("Results for ", "")
        datetime = parser.parse(datetime_str) 

        # Each result-con contains details of a single match
        matches = sublist.find_class("result-con")

        # Convert matches data from HTML into dictionary then 
        # store it in the pd.DataFrame
        sublist_matches = [
            {
                "date" : datetime.strftime(HLTVConfig["date_format"]), 
                **_parse_match_tree(match)
            } for match in matches
        ] 
        all_matches += sublist_matches

    return all_matches


def _parse_match_tree(html):
    """Extract results of each match from `div@class='result-con'` """
    # Team names 
    team_one = html.find_class("team1")[0].find_class("team")[0].text_content()
    team_two = html.find_class("team2")[0].find_class("team")[0].text_content() 
    
    # Scores
    scores = html.find_class("result-score")[0].text_content().split("-")
    score_one = scores[0].strip()
    score_two = scores[1].strip()

    # Event name
    event = html.find_class("event-name")[0].text_content().strip()

    # Best of
    map_text = html.find_class("map-text")[0].text_content().strip()

    # Match ID endpoint
    match_href = html.xpath(".//a")[0].get("href")
    match_id = match_href.split(sep="/")[2]

    # Number of stars
    stars = len(html.find_class("fa-star"))

    return {
        "match_id" : match_id,
        "team_1" : team_one,
        "team_2" : team_two,
        "score_1" : int(score_one),
        "score_2" : int(score_two),
        "map" : map_text,
        "event" : event,
        "stars" : stars,
    }

def get_past_matches_ids(skip=0, limit=100, query=None, **kwargs):
    """Return the URIs of matches in /results page.
    
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
        response = client.get(results_url, params=query.to_params())
        tree = html.fromstring(response.text)

        # Check for any results found
        results = tree.find_class("allres")
        if len(results) == 0:
            break

        # Extract the MATCH_ID from html page.
        # This has the form:
        #   /matches/{id}/{event-name}
        matches = results[0].find_class("result-con")
        matches_uris = [match.xpath(".//a")[0].get("href") for match in matches]
        matches_ids = [uri.split("/")[2] for uri in matches_uris]

        # Set the offset for the next request
        skip += len(matches_uris)

        # Adds to the accumulator
        all_matches_ids += matches_ids

    return all_matches_ids[:limit]
