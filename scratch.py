from src.database.data_update import customDataUpdate, smallDataUpdate

# customDataUpdate()
from src.database.database_creation import addExtraUrlToPlayerLinks, getAdvancedMetricsForTeams
from src.historical_data.nba_play_by_play_methods import fillGaps, teamSummaryDataFromFirstPointData
from src.live_data.display_bets import getAllOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import betfairOdds, getDailyOdds
from src.odds_and_statistics.prediction_enhancements import getFirstFieldGoalOrFirstPointStats

# teamSummaryDataFromFirstPointData(2014)
# teamSummaryDataFromFirstPointData(2015)
# teamSummaryDataFromFirstPointData(2016)
# teamSummaryDataFromFirstPointData(2017)
# teamSummaryDataFromFirstPointData(2018)
# teamSummaryDataFromFirstPointData(2019)
# teamSummaryDataFromFirstPointData(2020)
# teamSummaryDataFromFirstPointData(2021)

# getDailyOdds('MEM', 'GSW', '-135')
# smallDataUpdate()

getAdvancedMetricsForTeams('2014-15')