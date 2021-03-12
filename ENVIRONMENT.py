import os
from pathlib import Path

MAX_APPEARANCES = 9900

# Observed Values
HOME_SCORE_ODDS = 0.52111318 # backlogtodo slightly deflated due to 0.5 approximation of empty rows. May not apply w covid
HOME_TIP_WIN_ODDS = 0.51615348 # backlogtodo these are slightly deflated due to 0.5 approximation of empty rows
TIP_WINNER_SCORE_ODDS = 0.65495626 # backlogtodo these are slightly deflated due to 0.5 approximation of empty rows
# backlogtodo recalculate all of the uncertain data points above. This was originally done with a simple excel function on a fully concatenated csv of all seasons
# backlogtodo consider weighting for season recency
BANKROLL = 5000
REDUCTION_FACTOR = 0.7

# Testing Values
TIP_WIN = 0.73
MIN_APPEARANCES = 20

# Algorithm Comparison
ALGO_COMPARISON_PATH = Path(os.path.abspath('Data/JSON/algorithms/comparison.json'))
TS_PREDICTION_SUMMARIES_PATH = Path(os.path.abspath('Data/JSON/algorithms/trueskill/ts_prediction_summaries.json'))
GLICKO_PREDICTION_SUMMARIES_PATH = Path(os.path.abspath('Data/JSON/algorithms/glicko/glicko_prediction_summaries.json'))
ELO_PREDICTION_SUMMARIES_PATH = Path(os.path.abspath('Data/JSON/algorithms/elo/elo_prediction_summaries.json'))

# Trueskill Base values
BASE_TS_SIGMA = 25 / 3 # 8.333333333333334
BASE_TS_MU = 25
BASE_TS_RD = 25 * 25 / 3 / 3
BASE_TS_TAU = BASE_TS_SIGMA / 100 # 0.08333333333333334
BASE_TS_BETA = BASE_TS_SIGMA / 1.9 # 4.166666666666667 # todo this is the confidence interval for 76% certainty
# todo log the constants used in creating the summary
MIN_TS_APPEARANCES = MIN_APPEARANCES
TS_TIPOFF_ODDS_THRESHOLD = TIP_WIN
# Trueskill files
PLAYER_TRUESKILL_DICT_PATH = Path(os.path.abspath('Data/JSON/algorithms/trueskill/player_trueskill_dictionary.json'))

# Glicko Base values
BASE_GLICKO_MU = 1500
BASE_GLICKO_PHI = 350
BASE_GLICKO_SIGMA = 0.06
BASE_GLICKO_TAU = 1.0
MIN_GLICKO_APPEARANCES = MIN_APPEARANCES
GLICKO_TIPOFF_ODDS_THRESHOLD = TIP_WIN
# Epsilon can be adjusted for convergence speed/accuracy tradeoffs
# GLicko Files
PLAYER_GLICKO_DICT_PATH = Path(os.path.abspath('Data/JSON/algorithms/glicko/player_glicko_dictionary.json'))
SEASON_CSV_UNFORMATTED_PATH = os.path.abspath('Data/CSV/season_data/tipoff_and_first_score_details_{}_season.csv')

# Elo Base values
K_FACTOR = 10
BASE_ELO = 1200
BASE_ELO_BETA = 200
MIN_ELO_APPEARANCES = MIN_APPEARANCES
ELO_TIPOFF_ODDS_THRESHOLD = TIP_WIN
# Elo files
PLAYER_ELO_DICT_PATH = Path(os.path.abspath('Data/JSON/algorithms/elo/player_elo_dictionary.json'))

# Misc
LIVE_ODDS_API_1 = '5f92a0468c6f365be7db417f13d52742'
ALL_SEASONS_LIST = [2021] #[1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
SEASONS_LIST_SINCE_HORNETS = ALL_SEASONS_LIST[14:]
CURRENT_SEASON = ALL_SEASONS_LIST[-1]
CURRENT_TEAMS = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX', 'NYK',
                'BOS', 'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']

# Calculated Value Paths
ALL_SHOTS_BEFORE_FIRST_FG_PATH = Path(os.path.abspath('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json'))
SINGLE_SEASON_SHOTS_BEFORE_FIRST_FG_PATH = os.path.abspath('Data/JSON/Public_NBA_API/first_shots_data/{}_data.json')
# FIRST_FG_SUMMARY_PATH = Path(os.path.abspath('Data/JSON/Public_NBA_API/first_fg_summaries/first_fg_summary.json'))
FIRST_FG_SUMMARY_UNFORMATTED_PATH = os.path.abspath('Data/JSON/Public_NBA_API/first_fg_summaries/first_fg_summary_{}.json')
# FIRST_POINT_SUMMARY_PATH = Path(os.path.abspath('Data/JSON/Public_NBA_API/first_point_summary.json'))
FIRST_POINT_SUMMARY_UNFORMATTED_PATH = os.path.abspath('Data/JSON/Public_NBA_API/first_point_summaries/first_point_summary_{}.json')

# Raw Data Paths
PLAYER_TEAM_PAIRS_PATH = Path(os.path.abspath('Data/JSON/player_team_pairs.json'))
CURRENT_SEASON_CSV = Path(os.path.abspath('Data/CSV/season_data/tipoff_and_first_score_details_{}_season.csv'.format(CURRENT_SEASON)))
TEAM_NAMES_PATH = Path(os.path.abspath('Data/JSON/Public_NBA_API/teams.json'))
PLAYER_NAME_RELATIONSHIPS_PATH = Path(os.path.abspath('Data/JSON/player_name_relationships.json'))
BET_HISTORY_PATH = Path(os.path.abspath("Data/CSV/bet_history.csv"))
GAME_SUMMARY_UNFORMATTED_PATH = os.path.abspath('Data/CSV/season_summary_data/{}_allgames.csv')
TEAM_TIPPER_PAIRS_PATH = Path(os.path.abspath('Data/JSON/team_tipper_pairs.json'))
PLAYER_USAGE_PATH = Path(os.path.abspath("Data/JSON/player_usage.json"))

# NCAA Raw Data
NCAA_DATA_FOLDER = Path(os.path.abspath('Data/ncaahoopR_data-master'))
