import json

from nba_api.stats.endpoints import CommonPlayerInfo, leaguegamefinder
from nba_api.stats.static import teams
from nba_api.stats.static.players import find_players_by_full_name

import ENVIRONMENT
from src.utils import getDashDateAndHomeCodeFromGameCode, removeAllNonLettersAndLowercase
import pandas as pd

def getBballRefPlayerName(playerInUnknownFormat):
    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as playerDb:
        playersDict = json.load(playerDb)

    match = False
    playerLoweredLetterOnly = removeAllNonLettersAndLowercase(playerInUnknownFormat)
    for player in playersDict:
        if player['universalName'] == playerLoweredLetterOnly:
            match = True
            break
        elif playerInUnknownFormat in player['alternateNames']:
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat:
            match = True
            break
        elif player['nameWithComma'] == playerInUnknownFormat:
            match = True
            break
        elif player['bballRefCode'] == playerInUnknownFormat:
            match = True
            break

    if not match:
        raise ValueError("player", playerInUnknownFormat, "did not have a match")
    return player['bballRefCode']

# backlogtodo fix unmatched players in quarter counting
def getUniversalPlayerName(playerInUnknownFormat):
    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as playerDb:
        playersDict = json.load(playerDb)

    match = False
    playerLoweredLetterOnly = removeAllNonLettersAndLowercase(playerInUnknownFormat)
    undoPlayerCommaReversal = None

    if ',' in playerInUnknownFormat:
        head, tail = playerInUnknownFormat.split(',')
        undoPlayerCommaReversal = tail + head
        undoPlayerCommaReversal = removeAllNonLettersAndLowercase(undoPlayerCommaReversal)

    for player in playersDict:
        if player['bballRefCode'] == playerInUnknownFormat:
            match = True
            break
        elif playerInUnknownFormat in player['alternateNames']:
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat:
            match = True
            break
        elif player['nameWithComma'] == playerInUnknownFormat:
            match = True
            break
        elif player['universalName'] == playerLoweredLetterOnly:
            match = True
            break
        elif player['universalName'] == undoPlayerCommaReversal:
            match = True
            break
        elif removeAllNonLettersAndLowercase(player['nameWithComma']) == playerLoweredLetterOnly:
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat + " Jr.":
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat + " Sr.":
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat + " III":
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat + " IV":
            match = True
            break
        elif player['fullName'] == playerInUnknownFormat + " IV":
            match = True
            break
        try:
            if removeAllNonLettersAndLowercase(player['alternateNames'][0]) == undoPlayerCommaReversal:
                match = True
                break
        except:
            pass

    if not match:
        # raise ValueError("player", playerInUnknownFormat, "did not have a match")
        print("player", playerInUnknownFormat, "did not have a match, things may break")
        return playerInUnknownFormat
    return player['universalName']

def getPlayerCurrentTeam(universalPlayerName): # Returns a list
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as playerToTeamDb:
        playersDict = json.load(playerToTeamDb)
    return playersDict['2021'][universalPlayerName]['currentTeam']

def getUniversalTeamShortCode(teamInUnknownFormat):
    with open(ENVIRONMENT.TEAM_NAMES_PATH) as teamsDb:
        teamsDict = json.load(teamsDb)

    match = False
    for team in teamsDict:
        splitTeamList = teamInUnknownFormat.split(' ')
        if team['teamName'] == teamInUnknownFormat:
            match = True
            break
        elif len(splitTeamList[-1]) > 3 and splitTeamList[-1] in team['teamName']: # make sure it's not a short code before looking in
            match = True
            break
        elif team['simpleName'] == teamInUnknownFormat:
            match = True
            break
        elif team['location'] == teamInUnknownFormat:
            match = True
            break
        # elif team['slug'] == teamInUnknownFormat:
        #     break
        elif teamInUnknownFormat in team['alternateAbbreviations']:
            match = True
            break
        elif team['abbreviation'] == teamInUnknownFormat:
            match = True
            break
        elif team['bovadaId'] == teamInUnknownFormat:
            match = True
            break
    # Often format is "LA Clippers" or "DEN Nuggets" or "Nuggets"
    if not match:
        raise ValueError("team", teamInUnknownFormat, "did not have a match")
    return team['abbreviation']

def getTeamDictionaryFromShortCode(shortCode: str):
    shortCode = convertBballRefTeamShortCodeToNBA(shortCode)
    nbaTeams = teams.get_teams()
    teamDict = [team for team in nbaTeams if team['abbreviation'] == shortCode][0]
    return teamDict['id']

def getAllGamesForTeam(team_id: str):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    return gamefinder.get_data_frames()[0]

def _getGameObjFromDateAndTeamUsingLocalData(dateStr: str, shortCode: str):
    filePath = ENVIRONMENT.GAME_SUMMARY_UNFORMATTED_PATH
    filePath = filePath.format(shortCode)
    gameData = pd.read_csv(filePath)
    return gameData[gameData['GAME_DATE'] == dateStr]

# game date format is YYYY-MM-DD
def _getGameObjFromDateAndTeam(dateStr: str, shortCode: str):
    teamId = getTeamDictionaryFromShortCode(shortCode)
    allGames = getAllGamesForTeam(teamId)
    return allGames[allGames.GAME_DATE == str(dateStr)]

def getGameIdFromTeamAndDate(dateStr: str, shortCode: str):
    gameObj = _getGameObjFromDateAndTeam(dateStr, shortCode)
    return gameObj.GAME_ID.iloc[0]

def getGameIdByTeamAndDateFromStaticData(bballRefId: str):
    date, team = getDashDateAndHomeCodeFromGameCode(bballRefId)
    gameObj = _getGameObjFromDateAndTeamUsingLocalData(date, getUniversalTeamShortCode(team))
    return gameObj.GAME_ID.iloc[0]

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
    playerDict = find_players_by_full_name(name)[0]
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
    # playerName = getUniversalPlayerName(playerLink)
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as teamPairs:
        seasons = json.load(teamPairs)
        try:
            return seasons[str(season)][playerLink]['possibleTeams']
        except:
            raise ValueError("no match found for player", playerLink)
