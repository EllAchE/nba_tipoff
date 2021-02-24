import os
from pathlib import Path

TIPOFF_ODDS_THRESHOLD = 0.73
MIN_APPEARANCES = 20
MAX_APPEARANCES = 9900

# Observed Values
HOME_SCORE_ODDS = 0.52111318 # todo slightly deflated due to 0.5 approximation of empty rows. May not apply w covid
HOME_TIP_WIN_ODDS = 0.51615348 # todo these are slightly deflated due to 0.5 approximation of empty rows
TIP_WINNER_SCORE_ODDS = 0.65495626 # todo these are slightly deflated due to 0.5 approximation of empty rows
# todo recalculate all of the uncertain data points above. This was originally done with a simple excel function on a fully concatenated csv of all seasons
BANKROLL = 6170

# Trueskill Base values
BASE_SIGMA = 25 / 6
BASE_RATING = 25
BASE_DEVIATION = 25 * 25 / 3 / 3

# Path management
PLAYER_SKILL_DICT_PATH = Path(os.path.abspath('Data/JSON/player_skill_dictionary.json'))
PLAYER_TEAM_PAIR_DICT_PATH = Path(os.path.abspath('Data/JSON/player_team_pairs.json'))
PREDICTION_SUMMARIES_PATH = Path(os.path.abspath('Data/JSON/prediction_summaries.json'))
SEASON_CSV_NEEDING_FORMAT_PATH = os.path.abspath('Data/CSV/tipoff_and_first_score_details_{}_season.csv')
TEAM_CONVERSION_PATH = Path(os.path.abspath('Data/JSON/Public_NBA_API/teams.json'))
SHOTS_BEFORE_FIRST_SCORE_PATH = Path(os.path.abspath('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json'))

# Misc
LIVE_ODDS_API_1 = '5f92a0468c6f365be7db417f13d52742'
SEASONS_LIST = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
SEASONS_LIST_SINCE_HORNETS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
