import os
from urllib.parse import urljoin

from lxml import html

from hltv_api.client import HLTVClient
from hltv_api.common import HLTVConfig


def get_rounds_summary_by_match_id(match_id):
    # URL requires the event name but does not matter if it is
    # not the event corresponding to the ID
    match_id = str(match_id)
    uri = os.path.join("/", HLTVConfig["economy_uri"], match_id, "foo")

    client = HLTVClient()
    match_url = urljoin(HLTVConfig["base_url"], uri)
    response = client.get(match_url)

    tree = html.fromstring(response.text)

    history = [half.find_class("equipment-category-td")
               for half in tree.find_class("team-categories")]

    team_1_rounds = [*history[0], *history[2]]
    team_2_rounds = [*history[1], *history[3]]

    results = {}
    for i in range(0, 30):
        team_1_value = team_2_value = winner = None
        if i < len(team_1_rounds):
            team_1_value = team_1_rounds[i].get("title").strip("Equipment value: ")
            team_2_value = team_2_rounds[i].get("title").strip("Equipment value: ")

            winner = 1 if len(team_2_rounds[i].find_class("lost")) > 0 else 2

        results[f"{i + 1}_team_1_value"] = int(team_1_value)
        results[f"{i + 1}_team_2_value"] = int(team_2_value)
        results[f"{i + 1}_winner"] = int(winner)

    return results