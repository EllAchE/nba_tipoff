# This is where parameters can be tuned

# Tipoff Threshold Variables
import os

TIPOFF_ODDS_THRESHOLD = 0.73 # This will be deprecated
MIN_APPEARANCES = 20
MAX_APPEARANCES = 900

# Observed Values
HOME_SCORE_ODDS = 0.52111318 # todo slightly deflated due to 0.5 approximation of empty rows. May not apply w covid
HOME_TIP_WIN_ODDS = 0.51615348 # todo these are slightly deflated due to 0.5 approximation of empty rows
TIP_WINNER_SCORE_ODDS = 0.65495626 # todo these are slightly deflated due to 0.5 approximation of empty rows
# todo recalculate all of the uncertain data points above. This was originally done with a simple excel function on a fully concatenated csv of all seasons
BANKROLL = 6500

# Trueskill Base values
BASE_SIGMA = 25 / 6
BASE_RATING = 25
BASE_DEVIATION = 25 * 25 / 3 / 3
PLAYER_SKILL_DICT_PATH = os.path.abspath('Data/JSON/player_skill_dictionary.json')
PLAYER_TEAM_PAIR_DICT_PATH = os.path.abspath('Data/JSON/player_team_pairs.json')

# Misc
LIVE_ODDS_API_1 = '5f92a0468c6f365be7db417f13d52742'
SEASONS_LIST = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
