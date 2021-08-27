import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

class HLTVScraper():
    
    def __init__(self, base_url="https://www.hltv.org", ret_format="pandas"):
        self.base_url = base_url
        self.results_df = pd.DataFrame(columns=["event", "team_1", "team_2", "map", "score_1", "score_2"])

    def fetch_results(self, endpoint="/results", start_date=None, end_date=None, max_result_count=100):
        offset = 0
        result_rem_count = min(max_result_count - offset, 100) 
        new_row_count = 1

        while result_rem_count > 0 and new_row_count > 0:
            new_row_count = self.__fetch_results(endpoint, start_date, end_date, offset, result_rem_count)
            offset += new_row_count 
            result_rem_count = min(max_result_count - offset, 100) 
            
    def __fetch_results(self, endpoint, start_date=None, end_date=None, offset=0, max_result_count=100):
        url = urljoin(self.base_url, endpoint)
        query = {
            "startDate" : start_date,
            "endDate" : end_date,
            "offset" : offset
        }
        response = requests.get(url, params={k : v for k,v in query.items() if v is not None})
        tree = html.fromstring(response.text)

        # Total number of new rows
        new_row_count = 0

        # Each result sublist contains all matches for that particular day
        results_sublist = tree.find_class("allres")[0].find_class("results-sublist")
        
        # Iterate over the sublists and then individual matches
        for sublist in results_sublist:
            if max_result_count == 0:
                break

            datetime_obj = sublist.find_class("standard-headline")[0].text_content()
            datetime_str = datetime_obj.replace("Results for ", "")
            datetime = parser.parse(datetime_str) 

            # Each result-con contains details of a single match
            matches = sublist.find_class("result-con")

            # Slice to get the number of items wanted
            matches = matches[:max_result_count]
            max_result_count -= len(matches)
            new_row_count += len(matches)

            # Convert matches data from HTML into dictionary then 
            # store it in the pd.DataFrame
            sublist_matches = [self.__parse_match(match) for match in matches] 
            sublist_matches_df = pd.DataFrame(sublist_matches)
            sublist_matches_df["date"] = datetime.strftime("%d-%m-%Y")  
            self.results_df = self.results_df.append(sublist_matches_df, ignore_index=True)

        return new_row_count
    

    def __parse_match(self, html):
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

        return {
            "team_1" : team_one,
            "team_2" : team_two,
            "score_1" : score_one,
            "score_2" : score_two,
            "map" : map_text,
            "event" : event
        }
             
