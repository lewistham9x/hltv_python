import requests
import pandas as pd

from lxml import html
from urllib.parse import urljoin
from dateutil import parser 

from hltv_scraper.results import HLTVResults
from hltv_scraper.matches import HLTVMatches

class HLTVScraper():
    
    def __init__(self, base_url="https://www.hltv.org", ret_format="pandas"):
        self.base_url = base_url

    def fetch_matches(self, start_date=None, end_date=None, limit=None):
        client = HLTVMatches(base_url=self.base_url, endpoint="matches")

        return client.fetch_results(start_date=start_date, end_date=end_date, limit=limit)

    def fetch_results(self, start_date=None, end_date=None, limit=None, all_time=False):
        client = HLTVResults(base_url=self.base_url, endpoint="results")
        
        if all_time:
            return client.fetch_results(limit=limit)
        
        return client.fetch_results(start_date=start_date, end_date=end_date, limit=limit)

        
