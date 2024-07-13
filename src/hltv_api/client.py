import time
from urllib.parse import urljoin

import botasaurus as bt
from botasaurus import Browser

from hltv_api.common import HLTVConfig
from hltv_api.exceptions import HLTVRequestException
from urllib.parse import urljoin

from botasaurus.request import request, Request


class HLTVClient:
    def __init__(self, max_retry=3):
        self.max_retry = max_retry

    @request(max_retry=3)
    def _make_request(self, request: Request, url, params=None):
        response = request.get(url, params=params)
        response.raise_for_status()
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
