from src.database.data_update import customDataUpdate, smallDataUpdate

# customDataUpdate()
from src.database.database_creation import addExtraUrlToPlayerLinks
from src.historical_data.nba_play_by_play_methods import fillGaps
from src.live_data.display_bets import getAllOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import betfairOdds, getDailyOdds
from src.odds_and_statistics.prediction_enhancements import getFirstFieldGoalOrFirstPointStats

getFirstFieldGoalOrFirstPointStats(2014)
getFirstFieldGoalOrFirstPointStats(2015)
getFirstFieldGoalOrFirstPointStats(2016)
getFirstFieldGoalOrFirstPointStats(2017)
getFirstFieldGoalOrFirstPointStats(2018)
getFirstFieldGoalOrFirstPointStats(2019)
getFirstFieldGoalOrFirstPointStats(2020)
getFirstFieldGoalOrFirstPointStats(2021)

# getDailyOdds('MEM', 'GSW', '-135')
# smallDataUpdate()
