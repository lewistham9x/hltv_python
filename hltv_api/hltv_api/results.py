import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

from hltv_api.query import HLTVQuery
from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig

class HLTVResults():

    columns = ["match_id", "date", "event", "team_1", "team_2", "map", "score_1", "score_2", "stars"]

    def __init__(self, base_url=HLTVConfig["base_url"], endpoint=HLTVConfig["results_uri"]):
        self.base_url = base_url
        self.endpoint = endpoint
        self.client = HLTVClient(max_retry=3)

    def get_results(self, skip=0, limit=None, query=None, **kwargs): 
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
        

        Return
        ------
        pandas.DataFrame
        """

        query = query or HLTVQuery(**kwargs)                
        url = urljoin(self.base_url, self.endpoint)

        df = pd.DataFrame(columns=HLTVResults.columns)

        while (limit is None) or (len(df) < limit):  
            response = self.client.get(url, params=query.to_params())
            tree = html.fromstring(response.text)

            results = self.__parse_result_page(tree)
            batch_limit = limit - len(df)
            df = df.append(results[:batch_limit])

            skip += len(df)

        return df


    def __parse_result_page(self, html):
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
                    "date" : datetime.strftime("%Y-%m-%d"), 
                    **self.__parse_match_tree(match)
                } for match in matches
            ] 
            all_matches += sublist_matches
    
        return all_matches
    

    def __parse_match_tree(self, html):
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
