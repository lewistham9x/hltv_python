
def parse_map_stat_economy_page(tree):
    history = [half.find_class("equipment-category-td")
               for half in tree.find_class("team-categories")]

    team_1_rounds = [*history[0], *history[2]]
    team_2_rounds = [*history[1], *history[3]]

    results = {}
    for i in range(0, 30):
        team_1_value = team_2_value = winner = None
        if i < len(team_1_rounds):
            team_1_equipment = team_1_rounds[i].get("title")
            team_1_value = int(team_1_equipment.strip("Equipment value: "))\

            team_2_equipment = team_2_rounds[i].get("title").strip("Equipment value: ")
            team_2_value = int(team_2_equipment.strip("Equipment value: "))

            winner = 1 if len(team_2_rounds[i].find_class("lost")) > 0 else 2

        results[f"{i + 1}_team_1_value"] = team_1_value
        results[f"{i + 1}_team_2_value"] = team_2_value
        results[f"{i + 1}_winner"] = winner

    return results
