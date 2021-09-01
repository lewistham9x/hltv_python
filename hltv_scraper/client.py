import time
import requests

from datetime import datetime
from urllib.parse import urljoin

class HLTVClientException(Exception):
    """Base class for exception caused in this module."""
    pass

class HLTVRequestException(HLTVClientException):
    """Exception raised for when a request fails. """

    def __init__(self, message, status_code, response):
        self.message = message
        self.status_code = status_code
        self.response = response

class HLTVClient():

    def __init__(self, base_url="https://www.hltv.org", max_retry=1):
        self.base_url = base_url
        self.last_request_timestamp = None
        self.max_retry = 1

    def get(self, url, **kwargs):
        # TODO: Come up with algorithm to bypass rate limit
        attempt = 0
        response = None

        while attempt <= self.max_retry:
            if self.last_request_timestamp is not None:
                time_delta = datetime.now() - self.last_request_timestamp
                delta_seconds = time_delta.total_seconds() 

                if delta_seconds < 1:
                    time.sleep(1 - delta_seconds)
            
            # Update timestamp and retry if required
            response = requests.get(url, **kwargs)
            self.last_request_timestamp = datetime.now()
            
            # Return response if request succeeds
            if response.ok:
                return response
            
            # Otherwise retry
            attempt += 1

        raise HLTVRequestException(
            message=f"Failed to get data from HLTV after {attempt} attempt(s)",
            status_code=response.status_code,
            response=response
        )
  
    def search_team(self, search_term):
        url = urljoin(self.base_url, "searchTeam")
        return self.get(url, params={"term" : search_term})

