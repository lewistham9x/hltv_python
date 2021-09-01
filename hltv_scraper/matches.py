import time
import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

class HLTVMatches():

    columns = ["match_id", "date", "team_1", "team_2", "map", "team_1_ct", "team_2_t", "team_1_t", "team_2_ct", "starting_ct"]

    def __init__(self, base_url="https://www.hltv.org", endpoint="matches"):
        self.base_url = base_url
        self.endpoint = endpoint

    def get_matches_stats(self, start_date=None, end_date=None, skip=0, limit=None, batch_size=100):
        """Hits the HLTV webpage and gets the details for the matches.

        Parameter
        ---------
        start_date: Optional[str]
            Date of the first result with the format '%d-%m-%Y'

        end_date: Optional[str]
            Date of the last result with the format '%d-%m-%Y'

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

        """
        df = pd.DataFrame(columns=HLTVMatches.columns)

        while (limit is None) or (len(df) < limit):  
            batch_limit = batch_size if limit is None else min(batch_size, limit - len(df))
            match_ids = self.get_matches_ids(start_date=start_date, end_date=end_date, 
                                             skip=skip, limit=batch_limit)

            # Breaks if no result found
            if len(match_ids) == 0:
                break

            # Fetches match statistics using its ID
            matches_stats = [
                stat 
                for match_id in match_ids 
                    for stat in self.get_match_stats_by_id(match_id)
            ]
           
            df = df.append(matches_stats) 
            skip += len(match_ids) 
                
        return df

    
    def get_matches_ids(self, start_date=None, end_date=None, skip=0, limit=100):
        """Return the the links of {limit} matches.
        
        First, hits HLTV page /results?offset={skip}&startDate={start_date}&endDate={end_date}.
        Parses the HTML and gets the required number of matches, and extracts their IDs and hrefs.

        The return values are endpoints for the corresponding matches.

        Parameter
        ---------
        start_date: Optional[str]
            Date of the first result with the format '%d-%m-%Y'

        end_date: Optional[str]
            Date of the last result with the format '%d-%m-%Y'

        skip: Optional[int]
            The number of results to be skipped from being returned. 
            If not specified, do not skip any records.

        limit: Optional[int] 
            The maximum number of results to be returned. 
            If not specified, only return 100 records. This is the default number
            of matches displayed per page on HLTV.
            If NONE, return all the records found.
            
        """
        results_url = urljoin(self.base_url, "results")

        # Accumulator for all match ids
        all_matches_ids = []

        while (limit is None) or (len(all_matches_ids) < limit):
            response = requests.get(results_url, params={
                "startDate" : start_date,
                "endDate" : end_date,
                "offset" : skip
            })
            tree = html.fromstring(response.text)

            # Check for any results found
            results = tree.find_class("allres")
            if len(results) == 0:
                break

            # Extract the MATCH_ID from html page.
            # This has the form:
            #   /matches/{id}/{event-name}
            matches = results[0].find_class("result-con")
            matches_ids = [match.xpath(".//a")[0].get("href") for match in matches]

            # Set the offset for the next request
            skip += len(matches_ids)

            # Adds to the accumulator
            all_matches_ids += matches_ids

        return all_matches_ids[:limit]

    def get_match_stats_by_id(self, match_id):
        """Return the JSON details for the match by its match_id.

        Parameter
        ---------
        match_id: str
            HLTV endpoint that identifies the match. This usually has the format
            /matches/{id}/{event-name}

        Return
        ------
        List of dictionary objects containing the fields specified in {columns}
            
        """
        match_url = urljoin(self.base_url, match_id)
        response = requests.get(match_url)
        tree = html.fromstring(response.text)

        # Date
        date_obj = tree.find_class("date")[0].text_content()
        date_str = parser.parse(date_obj) 
        date = date_str.strftime("%d-%m-%Y")

        # Team names 
        team_one = tree.find_class("teamName")[0].text_content()
        team_two = tree.find_class("teamName")[1].text_content() 
       
        map_picks = tree.find_class("mapholder")
        maps = []

        for map_pick in map_picks:
            if len(map_pick.find_class("played")) == 0:
                continue
           
            maps.append({ 
                "match_id" : match_id,
                "date" : date, 
                "team_1" : team_one,
                "team_2" : team_two,
                **self.__parse_match_tree(map_pick)
            })
        return maps

    def __parse_match_tree(self, html):
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
            "map" : map_name,
            "team_1_t" : team_1_t,
            "team_1_ct" : team_1_ct,
            "team_2_t" : team_2_t,
            "team_2_ct" : team_2_ct,
            "starting_ct" : starting_ct
        }
