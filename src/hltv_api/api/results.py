from urllib.parse import urljoin
import pandas as pd
from lxml import html
import requests

from hltv_api.common import HLTVConfig
from hltv_api.pages.results import RESULTS_COLUMNS, parse_result_page
from hltv_api.query import HLTVQuery


class FlareSolverrClient:
    def __init__(self, flaresolverr_url="http://localhost:8191/v1"):
        self.flaresolverr_url = flaresolverr_url
        self.headers = {"Content-Type": "application/json"}

    def get(self, url, params=None):
        data = {"cmd": "request.get", "url": url, "maxTimeout": 60000}
        if params:
            data["url"] += "?" + "&".join(f"{k}={v}" for k, v in params.items())

        response = requests.post(self.flaresolverr_url, headers=self.headers, json=data)
        flaresolverr_response = response.json()

        if flaresolverr_response["status"] == "ok":
            return flaresolverr_response["solution"]
        else:
            raise Exception(
                f"FlareSolverr request failed: {flaresolverr_response['message']}"
            )


def get_results(base_url, skip=0, limit=None, query=None, **kwargs):
    query = query or HLTVQuery(**kwargs)
    url = urljoin(base_url, HLTVConfig["results_uri"])

    df = pd.DataFrame(columns=RESULTS_COLUMNS)

    client = FlareSolverrClient()
    while (limit is None) or (len(df) < limit):
        response = client.get(url, params={"offset": skip, **query.to_params()})
        tree = html.fromstring(response["response"])

        results = parse_result_page(tree)
        if len(results) == 0:
            break

        batch_limit = (
            len(results) if limit is None else min(len(results), limit - len(df))
        )

        df = df.append(results[:batch_limit])

        skip += len(df)

    return df


def get_past_matches_ids(base_url, skip=0, limit=100, query=None, **kwargs):
    results_url = urljoin(base_url, HLTVConfig["results_uri"])
    client = FlareSolverrClient()

    all_matches_ids = []

    query = query or HLTVQuery(**kwargs)

    while (limit is None) or (len(all_matches_ids) < limit):
        response = client.get(results_url, params={"offset": skip, **query.to_params()})

        tree = html.fromstring(response["response"])

        results = parse_result_page(tree)

        if len(results) == 0:
            break

        skip += len(results)

        all_matches_ids += [result["match_id"] for result in results]

    return all_matches_ids[:limit]
