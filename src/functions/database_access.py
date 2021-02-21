import json

from nba_api.stats.endpoints import CommonPlayerInfo, leaguegamefinder
from nba_api.stats.library.data import teams
from nba_api.stats.static.players import find_players_by_full_name

from src.functions.utils import getDashDateAndHomeCodeFromGameCode
# todo player to fullname to player code relationship
# https://www.w3schools.com/python/python_mysql_create_db.asp

def getUniversalShortCode(teamInUnknownFormat):
    with open('Data/JSON/Public_NBA_API/teams.json') as teamsDb:
        teamsDict = json.load(teamsDb)

    for team in teamsDict:
        splitTeamList = teamInUnknownFormat.split(' ')
        if team['teamName'] == teamInUnknownFormat:
            break
        elif len(splitTeamList[-1]) > 3 and splitTeamList[-1] in team['teamName']: # make sure it's not a short code before looking in
            break
        elif team['simpleName'] == teamInUnknownFormat:
            break
        elif team['location'] == teamInUnknownFormat:
            break
        # elif team['slug'] == teamInUnknownFormat:
        #     break
        elif teamInUnknownFormat in team['alternateAbbreviations']:
            break
        elif team['abbreviation'] == teamInUnknownFormat:
            break
    # todo add alternate abbreviation
    # Often format is "LA Clippers" or "DEN Nuggets" or "Nuggets"

    return team['abbreviation']
# todo make all of these universal conversions work
# todo use fuzzywuzzy on these matches

def getTeamDictionaryFromShortCode(shortCode: str):
    shortCode = convertBballRefTeamShortCodeToNBA(shortCode)
    nbaTeams = teams.get_teams()
    teamDict = [team for team in nbaTeams if team['abbreviation'] == shortCode][0]
    return teamDict['id']

def getAllGamesForTeam(team_id: str):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    return gamefinder.get_data_frames()[0]

# game date format is YYYY-MM-DD
def _getGameObjFromDateAndTeam(dateStr: str, shortCode: str):
    teamId = getTeamDictionaryFromShortCode(shortCode)
    allGames = getAllGamesForTeam(teamId)
    return allGames[allGames.GAME_DATE == str(dateStr)]

def getGameIdFromTeamAndDate(dateStr: str, shortCode: str):
    gameObj = _getGameObjFromDateAndTeam(dateStr, shortCode)
    return gameObj.GAME_ID.iloc[0]

def convertBballRefTeamShortCodeToNBA(shortCode: str):
    if shortCode == 'PHO':
        return 'PHX'
    if shortCode == 'BRK':
        return 'BKN'
    if shortCode == 'CHO':
        return 'CHA'
    return shortCode

def getCurrentPlayerTeam(player):
    # todo get a list of all active players for the season and map them to a bunch of possible aliases from different data sources
    pass

def findPlayerFullFromLastGivenPossibleFullNames(playerLastName, playerList):
    for player in playerList:
        if playerLastName == player["lastName"]:
            return player["fullName"]
    print('couldn\'t match player' + playerLastName)
    return playerLastName

def getGameIdFromBballRef(bballRefId):
    date, team = getDashDateAndHomeCodeFromGameCode(bballRefId)
    return getGameIdFromTeamAndDate(date, team)


def getPlayerTeamFromFullName(name):
    playerDict = find_players_by_full_name(name)[0] # todo deal with unicode breaking charanacters i.e. in the name bojan bogdonavic 'Bojan Bogdanović'
    playerId = playerDict['id']
    data = CommonPlayerInfo(player_id=playerId)
    playerData = data.common_player_info.get_data_frame()
    abbreviation = playerData['TEAM_ABBREVIATION'].iloc[0] # index of this if list is 19 (20th item)
    return abbreviation

def getPlayerTeamFromNbaApi(name):
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/commonplayerinfo.md
    pass

def getPlayerTeamInSeasonFromBballRefLink(playerLink, season, longCode=True):
    if longCode:
        playerLink = playerLink[11:]
    with open('Data/JSON/player_team_pairs.json') as teamPairs:
        seasons = json.load(teamPairs)
        try:
            return seasons[str(season)][playerLink]
        except:
            raise ValueError("no match found for player", playerLink)
