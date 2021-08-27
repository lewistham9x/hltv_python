import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

from hltv_scraper.results import HLTVResults

class HLTVScraper():
    
    def __init__(self, base_url="https://www.hltv.org", ret_format="pandas"):
        self.base_url = base_url

    def fetch_results_with_map_details(self, start_date=None, end_date=None, max_result_count=100):
        url = urljoin(self.base_url, endpoint)
        query = {
            "startDate" : start_date,
            "endDate" : end_date,
            "offset" : offset
        }
        response = requests.get(url, params={k : v for k,v in query.items() if v is not None})
        tree = html.fromstring(response.text)

        # Each result sublist contains all matches for that particular day
        results_sublist = tree.find_class("allres")[0].find_class("results-sublist")
        
        # Iterate over the sublists and then individual matches
        for sublist in results_sublist:

            datetime_obj = sublist.find_class("standard-headline")[0].text_content()
            datetime_str = datetime_obj.replace("Results for ", "")
            datetime = parser.parse(datetime_str) 

            # Each result-con contains details of a single match
            matches = sublist.find_class("result-con")

            # Convert matches data from HTML into dictionary then 
            # store it in the pd.DataFrame
            sublist_matches = [self.__parse_match(match) for match in matches] 
            sublist_matches_df = pd.DataFrame(sublist_matches)
            sublist_matches_df["date"] = datetime.strftime("%d-%m-%Y")  
            df = df.append(sublist_matches_df, ignore_index=True)

        return new_row_count, df
        

    def fetch_results(self, start_date=None, end_date=None, limit=None, all_time=False):
        client = HLTVResults(base_url=self.base_url, endpoint="results")
        
        if all_time:
            return client.fetch_results(limit=limit)
        
        return client.fetch_results(start_date=start_date, end_date=end_date, limit=limit)

        
