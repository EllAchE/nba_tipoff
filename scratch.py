from src.database.data_update import customDataUpdate, smallDataUpdate

# customDataUpdate()
from src.historical_data.nba_play_by_play_methods import fillGaps
from src.live_data.display_bets import getAllOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import betfairOdds, getDailyOdds
#
# getDailyOdds('BOS', 'SAC', '-105')

smallDataUpdate()