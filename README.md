## HLTV API


This is a part of my bigger CS:GO Machine Learning project, but might also be a 
useful module to scrape data from [HLTV](https://www.hltv.org/). 

This package offers built-in methods to get popular information from the website,
but also, methods to parse a particular page endpoint. Supported pages can be found
in corresponding files in [`src/hltv_api/pages/`]().

### Installation

```
pip install hltv-api
```

### Example Usage
Some useful methods:
1. results.

You can find more examples in [`examples/`]().

#### Simple usage
```python

from hltv_api import results

dataframe = results.get_results(limit=5, start_date="1st Sep 2021", end_date="2nd Sep 2021")

print(dataframe.head())
```
- And the output:


match_id|date|event|team_1|team_2|map|score_1|score_2|stars
--------|----|-----|------|------|---|-------|-------|-----
2346480|2021-02-09|ESEA Premier Season 36 North America|High Coast|Big Chillin|bo3|1|0|0
2346339|2021-02-09|BLAST Premier Spring Groups 2021|Vitality|Evil Geniuses|bo3|1|2|2
2346493|2021-02-09|ESEA Premier Season 36 Europe|FATE|GamerLegion|bo3|1|2|0
2346490|2021-02-09|ESEA Premier Season 36 Europe|forZe|SAW|bo3|1|2|1
2346494|2021-02-09|ESEA Premier Season 36 Europe|LDLC|Nemiga|bo3|1|2|0


#### Using more complex HLTV filters
```python
from hltv_api import stats
from hltv_api.query import HLTVQuery

query = HLTVQuery(team_names=["Natus Vincere", "Gambit"], player_names=["s1mple"], 
                  maps=["dust2", "inferno", "mirage"], require_all_teams=True)

dataframe = stats.get_matches_with_economy(limit=2, query=query)

print(dataframe.head())
```

- And the output:


index|match_id|map|team_1_id|team_2_id|starting_ct|1_team_1_value|1_team_2_value|1_winner|...|30_team_1_value|30_team_2_value|30_winner
-----|--------|---|---------|---------|-----------|--------------|--------------|--------|---|---------------|---------------|---------
0|2349632|ancient|6651|4608|2|4300|4200|2|...|NaN|NaN|NaN|NaN|NaN|NaN|NaN
6|2349630|mirage|6651|4608|2|3950|4200|1|...|NaN|NaN|NaN|NaN|NaN|NaN|NaN
