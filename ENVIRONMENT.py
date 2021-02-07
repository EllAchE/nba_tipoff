# This is where parameters can be tuned

# Tipoff Threshold Variables
TIPOFF_ODDS_THRESHOLD = 0.73 # This will be deprecated
MIN_APPEARANCES = 20
MAX_APPEARANCES = 900

# Observed Values
HOME_SCORE_ODDS = 0.52111318 # todo slightly deflated due to 0.5 approximation of empty rows. May not apply w covid
HOME_TIP_WIN_ODDS = 0.51615348 # todo these are slightly deflated due to 0.5 approximation of empty rows
TIP_WINNER_SCORE_ODDS = 0.65495626 # todo these are slightly deflated due to 0.5 approximation of empty rows
BANKROLL = 5000

# Trueskill Base values
BASE_SIGMA = 25 / 6
BASE_RATING = 25
BASE_DEVIATION = 25 * 25 / 3 / 3

LIVE_ODDS_API_1 = '5f92a0468c6f365be7db417f13d52742'
