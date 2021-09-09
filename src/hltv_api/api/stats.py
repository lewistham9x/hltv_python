import os
from urllib.parse import urljoin

from lxml import html

from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig
from hltv_api.pages.matches import parse_match_page
from hltv_api.pages.stats import parse_map_stat_economy_page


def get_economy_by_match_id(match_id):
    client = HLTVClient()

    # URL requires the event name but does not matter if it is
    # not the event corresponding to the ID
    match_id = str(match_id)
    match_uri = os.path.join(HLTVConfig["matches_uri"], match_id, "foo")
    match_url = urljoin(HLTVConfig["base_url"], match_uri)
    response = client.get(match_url)

    match_page = html.fromstring(response.text)
    match_details = parse_match_page(match_page)

    map_stats = []
    for map_played in match_details["maps"]:
        map_stats_uri = os.path.join(HLTVConfig["economy_uri"], str(map_played["map_stats_id"]), "foo")
        map_stats_url = urljoin(HLTVConfig["base_url"], map_stats_uri)
        map_stat_response = client.get(map_stats_url)

        tree = html.fromstring(map_stat_response.text)
        rounds = parse_map_stat_economy_page(tree)

        map_stats.append({
            **map_played,
            **rounds,
        })

    match_details["maps"] = map_stats
    return match_details
