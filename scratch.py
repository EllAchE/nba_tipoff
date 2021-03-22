import ENVIRONMENT
from src.database.data_update import customDataUpdate, smallDataUpdate

# customDataUpdate()
from src.database.database_creation import addExtraUrlToPlayerLinks, getAdvancedMetricsForTeams, \
    getShotBreakdownForTeams, addAdditionalMlColumnsSingleSeason
from src.historical_data.bball_reference_historical_data import updateCurrentSeasonRawGameData
from src.historical_data.nba_play_by_play_methods import fillGaps, teamSummaryDataFromFirstPointData, \
    getAllFirstPossessionStatisticsIncrementally
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

addAdditionalMlColumnsSingleSeason(2015)

# getDailyOdds('CLE', 'TOR', '-107')
# smallDataUpdate()
# getAllOddsAndDisplayByEv(fanduelToday=True)
# updateCurrentSeasonRawGameData()
