import logging

from dateutil import parser

from hltv_api.common import HLTVConfig

logger = logging.getLogger(__name__)


def parse_match_page(tree):
    """Parses overview page for a match.
    Usually, endpoint is of the form:
        /matches/{id}/{team-1-vs-team-2-event-name}

    Parameter
    ---------
    tree: lxml.html.HtmlElement
        HTML of the webpage

    Return
    ------
    Dictionary containing all extractable information.

    """
    # Date
    date_obj = tree.find_class("date")[0].text_content()
    date_str = parser.parse(date_obj)
    date = date_str.strftime(HLTVConfig["date_format"])

    # Event
    event_uri = tree.find_class("event")[0].xpath(".//a")[0].get("href")
    event_id = event_uri.split("/")[2]

    # Match URL
    match_url = tree.xpath(".//head/link[contains(@rel, 'canonical')]")[0].get("href")
    match_id = match_url.rsplit("/")[-2]

    # Team 1
    team_one = tree.find_class("teamName")[0].text_content()
    team_one_uri = tree.find_class("team1-gradient")[0].xpath(".//a")[0].get("href")
    team_one_id = team_one_uri.split(sep="/")[2]

    # Team 2
    team_two = tree.find_class("teamName")[1].text_content()
    team_two_uri = tree.find_class("team2-gradient")[0].xpath(".//a")[0].get("href")
    team_two_id = team_two_uri.split(sep="/")[2]

    # Maps played
    map_picks = tree.find_class("mapholder")
    maps = [parse_mapholder_div(map_pick)
            for map_pick in map_picks if len(map_pick.find_class("results-stats")) > 0]

    return {
        "date": date,
        "match_id": match_id,
        "event_id": event_id,
        "team_1": team_one,
        "team_1_id": team_one_id,
        "team_2": team_two,
        "team_2_id": team_two_id,
        "maps": maps
    }


def parse_mapholder_div(tree):
    """Parses the HTML for a 'mapholder' class.

    Parameter
    ---------
    tree: lxml.html.HtmlElement
        The section in the HTML page for each map. This is normally
        <div class="mapholder"> ... </div>
    
    Return
    ------
    Dictionary object with the specified fields 
    """
    # Name of current map
    map_name = tree.find_class("mapname")[0].text_content()

    # ID of the map statistics
    map_stats_uri = tree.find_class("results-stats")[0].get("href")
    map_stats_id = map_stats_uri.rsplit("/")[-2]

    # Scores for CT and T sides for each half
    ct_scores = [score.text_content() for score in tree.find_class("ct")]
    t_scores = [score.text_content() for score in tree.find_class("t")]

    # Team 1 starts on CT or T side
    team_1_starting = tree.find_class("results-center-half-score")[0].xpath(".//span")[1].get("class")

    # 1 iff team_1 starts on CT, 2 otherwise (team_2 starts on CT)
    if team_1_starting == "ct":
        starting_ct = 1

        team_1_ct = ct_scores[0]
        team_1_t = t_scores[1]

        team_2_ct = ct_scores[1]
        team_2_t = t_scores[0]
    else:
        starting_ct = 2

        team_1_ct = ct_scores[1]
        team_1_t = t_scores[0]

        team_2_ct = ct_scores[0]
        team_2_t = t_scores[1]

    return {
        "map": map_name.lower(),
        "map_stats_id": int(map_stats_id),
        "team_1_t": int(team_1_t),
        "team_1_ct": int(team_1_ct),
        "team_2_t": int(team_2_t),
        "team_2_ct": int(team_2_ct),
        "starting_ct": starting_ct
    }
