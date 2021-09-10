"""
We will demonstrate how you can use this package to fetch data from HLTV webpage.

In this example, we'd like to fetch the results of:
    - matches on 9th September 2021
    - rated 3 stars
    - with economy rounds breakdown

"""

import os
from datetime import datetime

from hltv_api import stats

df = stats.get_matches_with_economy(
    start_date=datetime(year=2021, month=9, day=9),
    end_date=datetime(year=2021, month=9, day=9),
    stars=3,
)
path = os.path.join(os.path.dirname(__file__), "output.csv")
df.to_csv(path)
