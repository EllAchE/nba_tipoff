import ENVIRONMENT
from src.historical_data.bball_reference_historical_data import updateCurrentSeasonRawGameData
from src.database.database_creation import saveActivePlayersTeams, getAllGameData, createPlayerNameRelationship
from src.historical_data.nba_play_by_play_methods import getAllFirstPossessionStatisticsIncrementally, \
    teamSummaryDataFromFirstPointData, saveAllHistoricalStarters
from src.odds_and_statistics.prediction_enhancements import getCurrentSeasonUsageRate, \
    getFirstFieldGoalOrFirstPointStats
from src.rating_algorithms.trueskill_data_processing import updateTrueSkillDictionaryFromLastGame, \
    calculateTrueSkillDictionaryFromZero


def updateCurrentSeasonPlayerData():
    createPlayerNameRelationship(ENVIRONMENT.CURRENT_SEASON)
    saveActivePlayersTeams(ENVIRONMENT.CURRENT_SEASON)

def updateAllDataLongTermIncluded():
    updateCurrentSeasonRawGameData()
    createPlayerNameRelationship(startSeason=ENVIRONMENT.ALL_SEASONS_LIST[0]) # proxies a database with player names
    saveActivePlayersTeams(start_season=ENVIRONMENT.ALL_SEASONS_LIST[0]) # updates who a player has played for. Does not need to be run often
    getAllGameData() # saves data to Data/CSV/season_summary_data and fetches game headers for every game, basically
    updateTrueSkillDictionaryFromLastGame()
    getAllFirstPossessionStatisticsIncrementally(ENVIRONMENT.CURRENT_SEASON)
    getFirstFieldGoalOrFirstPointStats(ENVIRONMENT.CURRENT_SEASON) # Since Hornets became a team
    teamSummaryDataFromFirstPointData(ENVIRONMENT.CURRENT_SEASON)

    saveAllHistoricalStarters()
    getCurrentSeasonUsageRate()

# todo hook up trueskill from last game
def smallDataUpdate():
    updateCurrentSeasonRawGameData()
    calculateTrueSkillDictionaryFromZero()
    # getAllFirstPossessionStatisticsIncrementally(ENVIRONMENT.CURRENT_SEASON)
    # getFirstFieldGoalOrFirstPointStats(ENVIRONMENT.CURRENT_SEASON) # Since Hornets became a team
    # teamSummaryDataFromFirstPointData(ENVIRONMENT.CURRENT_SEASON)

def customDataUpdate():
    createPlayerNameRelationship(startSeason=ENVIRONMENT.ALL_SEASONS_LIST[0]) # proxies a database with player names
    saveActivePlayersTeams(start_season=ENVIRONMENT.ALL_SEASONS_LIST[0]) # updates who a player has played for. Does not need to be run often