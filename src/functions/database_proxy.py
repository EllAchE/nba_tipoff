import json

from nba_api.stats.endpoints import CommonPlayerInfo
from nba_api.stats.static.players import find_players_by_full_name

from src.functions.nba_public import getGameIdFromTeamAndDate
from src.functions.utils import getDashDateAndHomeCodeFromGameCode


def getUniversalShortCode(teamFormat):
    shortCode = 'BOS'
    return shortCode
# todo make all of these universal conversions work


def getCurrentPlayerTeam(player):
    # todo get a list of all active players for the season and map them to a bunch of possible aliases from different data sources
    pass

def convertBballRefTeamShortCodeToNBA(shortCode: str):
    if shortCode == 'PHO':
        return 'PHX'
    if shortCode == 'BRK':
        return 'BKN'
    if shortCode == 'CHO':
        return 'CHA'
    return shortCode


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
