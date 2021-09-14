import random
import time
from urllib.parse import urljoin

import requests
from requests import Request, Session

from hltv_api.common import HLTVConfig
from hltv_api.exceptions import HLTVRequestException


class HLTVClient():
    USER_AGENTS = ['hltv-api 0.1', 'python-request', 'request']

    def __init__(self, max_retry=3):
        self.prev_response = None

        if max_retry > 0:
            self.max_retry = max_retry

    def get(self, url, **kwargs):
        # TODO: Come up with algorithm to bypass rate limit
        attempt = 0

        session = Session()
        request = Request('GET', url=url, **kwargs)

        while attempt <= self.max_retry:
            prepped = session.prepare_request(request)
            response = session.send(prepped)

            if self.prev_response is not None:
                self.__handle_failed_request(prepped, response, only_retry_after=attempt == self.max_retry)

            # Return response if request succeeds
            if response.ok:
                return response

            # Update timestamp and retry if required
            self.prev_response = response

            # Otherwise retry
            attempt += 1

        raise HLTVRequestException(
            message=f"Failed to get data from HLTV after {attempt} attempt(s)",
            status_code=response.status_code,
            response=response
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

    def __handle_failed_request(self, request, response, only_retry_after=False):
        if only_retry_after:
            retry_after = response.headers.get("Retry-After", "10")
            time.sleep(int(retry_after))

        # TODO: Implement API throttling mechanism
        request.headers.update({
            'User-Agent', HLTVClient.USER_AGENTS[random.randint(0, len(HLTVClient.USER_AGENTS))]
        })


