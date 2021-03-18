import ENVIRONMENT
from src.historical_data.bball_reference_historical_data import updateCurrentSeasonRawGameData
from src.database.database_creation import saveActivePlayersTeams, getAllGameData, createPlayerNameRelationship
from src.historical_data.nba_play_by_play_methods import getAllFirstPossessionStatisticsIncrementally, \
    teamSummaryDataFromFirstPointData
from src.rating_algorithms.trueskill_data_processing import updateTrueSkillDictionaryFromLastGame
# todo add auto updates to all data, meaning:
# raw game data
# first point data
# rating dictionary
# players, player team pairs, etc. (triggered on a break)

def updateAllDataLongTermIncluded():
    updateCurrentSeasonRawGameData()
    createPlayerNameRelationship(ENVIRONMENT.ALL_SEASONS_LIST[0]) # proxies a database with player names
    saveActivePlayersTeams(ENVIRONMENT.ALL_SEASONS_LIST[0]) # updates who a player has played for. Does not need to be run often
    getAllGameData() # saves data to Data/CSV/season_summary_data and fetches game headers for every game, basically
    updateTrueSkillDictionaryFromLastGame()
    getAllFirstPossessionStatisticsIncrementally(ENVIRONMENT.CURRENT_SEASON)
    teamSummaryDataFromFirstPointData(ENVIRONMENT.CURRENT_SEASON)
    # saveAllHistoricalStarters()

def smallDataUpdate():
    updateCurrentSeasonRawGameData()
    updateTrueSkillDictionaryFromLastGame()
    getAllFirstPossessionStatisticsIncrementally(ENVIRONMENT.CURRENT_SEASON)