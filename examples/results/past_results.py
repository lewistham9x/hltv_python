"""
We will demonstrate how you can use this package to fetch data from HLTV webpage.

In this example, we'd like to fetch the results of:
    - 30 most recent match-ups
    - between Natus Vincere and Faze
    - in the period between 2016 and 2020
    - with NiKo in the lineup

"""
import os

from datetime import datetime

from hltv_api import results
from hltv_api.query import HLTVQuery

query = HLTVQuery(
    # Start of search range
    start_date=datetime(year=2016, month=1, day=1),

    # End of search range (inclusive)
    end_date=datetime(year=2020, month=12, day=31),

    # Teams required
    team_names=["Natus Vincere", "Faze"],

    # Players required
    player_names=["NiKo"],

    # Require both NaVi and Faze to be present
    require_all_teams=True
)

df = results.get_results(limit=30, query=query)
path = os.path.join(os.path.dirname(__file__), "output.csv")
df.to_csv(path)
