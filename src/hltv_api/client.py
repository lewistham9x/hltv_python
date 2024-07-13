import time
from urllib.parse import urljoin
import requests

from hltv_api.common import HLTVConfig
from hltv_api.exceptions import HLTVRequestException


class HLTVClient:
    USER_AGENTS = ["hltv-api 0.1", "python-request", "request"]

    def __init__(self, max_retry=3):
        self.prev_response = None
        self.max_retry = max_retry if max_retry > 0 else 3
        self.url = "http://localhost:8191/v1"
        self.headers = {"Content-Type": "application/json"}

    def get(self, url, **kwargs):
        attempt = 0
        response = None

        while attempt <= self.max_retry:
            data = {"cmd": "request.get", "url": url, "maxTimeout": 60000}
            data.update(kwargs)

            response = requests.post(self.url, headers=self.headers, json=data)

            if response.ok:
                return response

            self.prev_response = response
            attempt += 1

            if attempt <= self.max_retry:
                self.__handle_failed_request(only_retry_after=attempt == self.max_retry)

        raise HLTVRequestException(
            f"Failed to get data from HLTV after {attempt} attempt(s)",
            response.status_code if response else None,
            response,
        )

    def search_team(self, search_term):
        url = urljoin(HLTVConfig["base_url"], HLTVConfig["search_teams_uri"])
        response = self.get(url, params={"term": search_term})
        return response.json()

    def search_player(self, search_term):
        url = urljoin(HLTVConfig["base_url"], HLTVConfig["search_players_uri"])
        response = self.get(url, params={"term": search_term})
        return response.json()

    def search_event(self, search_term):
        url = urljoin(HLTVConfig["base_url"], HLTVConfig["search_events_uri"])
        response = self.get(url, params={"term": search_term})
        return response.json()

    def __handle_failed_request(self, only_retry_after=False):
        if only_retry_after and self.prev_response is not None:
            retry_after = self.prev_response.headers.get("Retry-After", "10")
            time.sleep(int(retry_after))

        # TODO: Implement API throttling mechanism
