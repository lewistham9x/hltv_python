import time
from urllib.parse import urljoin

import botasaurus as bt
from botasaurus import Browser

from hltv_api.common import HLTVConfig
from hltv_api.exceptions import HLTVRequestException


class HLTVClient:
    def __init__(self, max_retry=3):
        self.browser = Browser(
            max_retry=max_retry,
            request_interval=1,  # 1 second interval between requests
            retry_wait_time=10,  # Wait 10 seconds before retrying
        )

    @bt.browser.get()
    def _make_request(self, url, params=None):
        response = self.browser.get(url, params=params)
        if not response.ok:
            raise HLTVRequestException(
                f"Failed to get data from HLTV", response.status_code, response
            )
        return response.json()

    def search_team(self, search_term):
        url = urljoin(HLTVConfig["base_url"], HLTVConfig["search_teams_uri"])
        return self._make_request(url, params={"term": search_term})

    def search_player(self, search_term):
        url = urljoin(HLTVConfig["base_url"], HLTVConfig["search_players_uri"])
        return self._make_request(url, params={"term": search_term})

    def search_event(self, search_term):
        url = urljoin(HLTVConfig["base_url"], HLTVConfig["search_events_uri"])
        return self._make_request(url, params={"term": search_term})
