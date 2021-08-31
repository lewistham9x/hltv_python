import time
import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

class HLTVMatches():

    columns = ["match_href", "date", "team_1", "team_2", "map", "team_1_ct", "team_2_t", "team_1_t", "team_2_ct", "starting_ct"]

    def __init__(self, base_url="https://www.hltv.org", endpoint="matches", delay=1):
        self.base_url = base_url
        self.endpoint = endpoint

    def fetch_results(self, start_date=None, end_date=None, limit=None):
        """Hits the HLTV webpage and gets the details for the matches """
        df = pd.DataFrame(columns=HLTVMatches.columns)

        offset = 0
        new_row_count = 1

        if limit is not None:
            result_rem_count = min(limit - offset, 100) 
        
        while new_row_count > 0 and (limit is None or result_rem_count > 0):
            match_ids = self.__fetch_matches_href(start_date, end_date, offset, result_rem_count)
            
            for match_id in match_ids:
                try:
                    results = self.__fetch_match(match_id) 
                    df = df.append(results)
                except:
                    return df
                

            offset += len(match_ids) 
        
            # If limit is set, work out how many more records are required
            if limit is not None:
                result_rem_count = min(limit - offset, 100) 
                
        return df

    
    def __fetch_matches_href(self, start_date=None, end_date=None, offset=0, limit=100):
        """Return the the links of {limit} matches.
        
        First, hits HLTV page /results?offset={offset}&startDate={start_date}&endDate={end_date}.
        Parses the HTML and gets the required number of matches, and extracts their IDs and hrefs.

        The return values are endpoints for the corresponding matches.
            
        """
        results_url = urljoin(self.base_url, "results")

        query = {
            "startDate" : start_date,
            "endDate" : end_date,
            "offset" : offset
        }
        response = requests.get(
            results_url, 
            params={k : v for k,v in query.items() if v is not None}
        )
        tree = html.fromstring(response.text)
        result_list = tree.find_class("allres")[0].find_class("result-con")
        match_ids_list = [res.xpath(".//a")[0].get("href") for res in result_list]

        return match_ids_list[:limit]

    def __fetch_match(self, match_id):
        """Return the JSON details for the match by its match_id.

        Parameter
        ---------
        match_id: HLTV endpoint that identifies the match. This usually has the format
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
                "match_href" : match_id,
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
