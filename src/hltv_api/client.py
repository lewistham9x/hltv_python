import random
import time
from urllib.parse import urljoin

import cloudscraper

from hltv_api.common import HLTVConfig
from hltv_api.exceptions import HLTVRequestException


class HLTVClient:
    def __init__(self, max_retry=3, proxies=None):
        self.prev_response = None
        self.max_retry = max_retry if max_retry > 0 else 3
        self.proxies = proxies
        self.current_proxy = None
        self.scraper = self._create_scraper()

    def _create_scraper(self):
        if self.proxies:
            self.current_proxy = self._get_random_proxy()
            return cloudscraper.create_scraper(proxies=self.current_proxy)
        return cloudscraper.create_scraper()

    def _get_random_proxy(self):
        if isinstance(self.proxies, list):
            return random.choice(self.proxies)
        elif isinstance(self.proxies, dict):
            return self.proxies
        else:
            raise ValueError("Proxies must be a list of proxy strings or a dictionary.")

    def _rotate_proxy(self):
        if isinstance(self.proxies, list):
            self.current_proxy = self._get_random_proxy()
            self.scraper = self._create_scraper()

    def get(self, url, **kwargs):
        attempt = 0
        response = None

        while attempt <= self.max_retry:
            try:
                response = self.scraper.get(url, **kwargs)
                if response.ok:
                    return response
            except cloudscraper.exceptions.CloudflareChallengeError as e:
                print(f"Cloudflare challenge encountered: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

            self.prev_response = response
            attempt += 1

            if self.proxies:
                self._rotate_proxy()

            time.sleep(random.uniform(1, 3))

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
