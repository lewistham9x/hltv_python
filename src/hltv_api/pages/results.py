from dateutil import parser

from hltv_api.common import HLTVConfig

RESULTS_COLUMNS = ["match_id", "date", "event", "team_1", "team_2", "map", "score_1", "score_2", "stars"]


def parse_result_page(tree):
    """Parse and extract results from a `/results` page"""
    all_matches = []

    # Each result sublist contains all matches for that particular day
    results = tree.find_class("allres")
    if len(results) == 0:
        return all_matches

    results_sublists = results[0].find_class("results-sublist")


    # Iterate over the sub-lists and then individual matches
    for sublist in results_sublists:
        datetime_obj = sublist.find_class("standard-headline")[0].text_content()
        datetime_str = datetime_obj.replace("Results for ", "")
        datetime = parser.parse(datetime_str)

        # Each result-con contains details of a single match
        matches = sublist.find_class("result-con")

        # Convert matches data from HTML into dictionary then 
        # store it in the pd.DataFrame
        sublist_matches = [
            {
                "date": datetime.strftime(HLTVConfig["date_format"]),
                **parse_result_con_div(match)
            } for match in matches
        ]
        all_matches += sublist_matches

    return all_matches


def parse_result_con_div(tree):
    """Extract results of each match from `div@class='result-con'` """
    # Team names 
    team_one = tree.find_class("team1")[0].find_class("team")[0].text_content()
    team_two = tree.find_class("team2")[0].find_class("team")[0].text_content()

    # Scores
    scores = tree.find_class("result-score")[0].text_content().split("-")
    score_one = scores[0].strip()
    score_two = scores[1].strip()

    # Event name
    event = tree.find_class("event-name")[0].text_content().strip()

    # Best of
    map_text = tree.find_class("map-text")[0].text_content().strip()

    # Match ID endpoint
    match_href = tree.xpath(".//a")[0].get("href")
    match_id = match_href.split(sep="/")[2]

    # Number of stars
    stars = len(tree.find_class("fa-star"))

    return {
        "match_id": match_id,
        "team_1": team_one,
        "team_2": team_two,
        "score_1": int(score_one),
        "score_2": int(score_two),
        "map": map_text,
        "event": event,
        "stars": stars,
    }
