from nba_api.stats.endpoints import TeamDashboardByGameSplits
import ENVIRONMENT
from src.database.data_update import customDataUpdate, smallDataUpdate, updateLongTermData
from src.database.database_creation import addExtraUrlToPlayerLinks, getAdvancedMetricsForTeams, \
    getShotBreakdownForTeams, addAdditionalMlColumnsSingleSeason, concatCsv, getPlusMinusForTeams
from src.historical_data.bball_reference_historical_data import updateCurrentSeasonRawGameData
from src.historical_data.nba_play_by_play_methods import fillGaps, teamSummaryDataFromFirstPointData, \
    getAllFirstPossessionStatisticsIncrementally
from src.live_data.display_bets import getAllOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import betfairOdds, getDailyOdds
from src.odds_and_statistics.odds_calculator import kellyBetReduced, getArbitrageRatiosTwoLines, \
    sysEMainDiagonalVarsNeg1Fill, \
    americanToDecimal, costFor1, americanToRatio, checkForArbitrageAnyNumberOfLines, checkForArbitrageInRetrievedOdds
from src.odds_and_statistics.prediction_enhancements import getFirstFieldGoalOrFirstPointStats

# teamSummaryDataFromFirstPointData(2014)
# teamSummaryDataFromFirstPointData(2015)
# teamSummaryDataFromFirstPointData(2016)
# teamSummaryDataFromFirstPointData(2017)
# teamSummaryDataFromFirstPointData(2018)
# teamSummaryDataFromFirstPointData(2019)
# teamSummaryDataFromFirstPointData(2020)
# teamSummaryDataFromFirstPointData(2021)


# calculateTrueSkillDictionaryFromZero()
# calculateGlickoDictionaryFromZero()
# calculateEloDictionaryFromZero()
# addAdditionalMlColumnsSingleSeason(2013)
# addAdditionalMlColumnsSingleSeason(2014)
# addAdditionalMlColumnsSingleSeason(2015)
# addAdditionalMlColumnsSingleSeason(2016)
# addAdditionalMlColumnsSingleSeason(2017)
# addAdditionalMlColumnsSingleSeason(2018)
# addAdditionalMlColumnsSingleSeason(2019)
# addAdditionalMlColumnsSingleSeason(2020)

# getArbitrageRatiosTwoLines('-110', '+134', printResult=True)

# concatCsv('all_ml_cols.csv', ENVIRONMENT.ML_COLS_FOLDER_PATH)

checkForArbitrageInRetrievedOdds()

getDailyOdds('NOP', 'PHI', '-120')
# getAllOddsAndDisplayByEv(bovada=True)
# smallDataUpdate()
# getAllOddsAndDisplayByEv(fanduelToday=True)
# updateCurrentSeasonRawGameData()

# XGBoost(2020)
# getPlusMinusForTeams(2020)
# addAdditionalMlColumnsSingleSeason(2013)
# addAdditionalMlColumnsSingleSeason(2016)
# addAdditionalMlColumnsSingleSeason(2017)
# addAdditionalMlColumnsSingleSeason(2018)
# addAdditionalMlColumnsSingleSeason(2019)
# addAdditionalMlColumnsSingleSeason(2020)