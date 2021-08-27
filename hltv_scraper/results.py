import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

class HLTVResults():

    columns = ["match_href", "event", "team_1", "team_2", "map", "score_1", "score_2", "stars"]

    def __init__(self, base_url="https://www.hltv.org", endpoint="results"):
        self.base_url = base_url
        self.endpoint = endpoint
        self.base_path = urljoin(base_url, endpoint)

    def fetch_results(self, start_date=None, end_date=None, limit=None):
        df = pd.DataFrame(columns=HLTVResults.columns)
        
        offset = 0
        new_row_count = 1

        if limit is not None:
            result_rem_count = min(limit - offset, 100) 
        
        while new_row_count > 0 and (limit is None or result_rem_count > 0):
            new_row_count, df = self.__fetch_results(df, start_date, end_date, offset, result_rem_count)
            offset += new_row_count
        
            # If limit is set, work out how many more records are required
            if limit is not None:
                result_rem_count = min(limit - offset, 100) 
                
        return df
    

    def __fetch_results(self, df, start_date=None, end_date=None, offset=0, limit=100):
        query = {
            "startDate" : start_date,
            "endDate" : end_date,
            "offset" : offset
        }
        response = requests.get(
            self.base_path, 
            params={k : v for k,v in query.items() if v is not None}
        )
        tree = html.fromstring(response.text)

        # Total number of new rows
        new_row_count = 0

        # Each result sublist contains all matches for that particular day
        results_sublist = tree.find_class("allres")[0].find_class("results-sublist")
        
        # Iterate over the sublists and then individual matches
        for sublist in results_sublist:
            if limit == 0:
                break

            datetime_obj = sublist.find_class("standard-headline")[0].text_content()
            datetime_str = datetime_obj.replace("Results for ", "")
            datetime = parser.parse(datetime_str) 

            # Each result-con contains details of a single match
            matches = sublist.find_class("result-con")

            # Slice to get the number of items wanted
            matches = matches[:limit]
            limit -= len(matches)
            new_row_count += len(matches)

            # Convert matches data from HTML into dictionary then 
            # store it in the pd.DataFrame
            sublist_matches = [self.__parse_match_tree(match) for match in matches] 
            sublist_matches_df = pd.DataFrame(sublist_matches)
            sublist_matches_df["date"] = datetime.strftime("%d-%m-%Y")  
            df = df.append(sublist_matches_df, ignore_index=True)

        return new_row_count, df
    

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

        # Number of stars
        stars = len(html.find_class("fa-star"))

        return {
            "match_href" : match_href,
            "team_1" : team_one,
            "team_2" : team_two,
            "score_1" : score_one,
            "score_2" : score_two,
            "map" : map_text,
            "event" : event,
            "stars" : stars
        }
