import json

from nba_api.stats.endpoints import CommonPlayerInfo, leaguegamefinder
from nba_api.stats.static import teams
from nba_api.stats.static.players import find_players_by_full_name

import ENVIRONMENT
from src.utils import getDashDateAndHomeCodeFromGameCode, removeAllNonLettersAndLowercase
import pandas as pd

# backlogtodo fix unmatched players in quarter counting
def getUniversalPlayerName(playerInUnknownFormat, bballRefName=False):
    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as playerDb:
        playersDict = json.load(playerDb)

    playerLoweredLetterOnly = removeAllNonLettersAndLowercase(playerInUnknownFormat)
    undoPlayerCommaReversal = None

    if ',' in playerInUnknownFormat:
        head, tail = playerInUnknownFormat.split(',')
        undoPlayerCommaReversal = tail + head
        undoPlayerCommaReversal = removeAllNonLettersAndLowercase(undoPlayerCommaReversal)

    match = False
    for player in playersDict:
        if player['bballRefCode'] == playerInUnknownFormat:
            match = True
        elif playerInUnknownFormat in player['alternateNames']:
            match = True
        elif player['fullName'] == playerInUnknownFormat:
            match = True
        elif player['nameWithComma'] == playerInUnknownFormat:
            match = True
        elif player['universalName'] == playerLoweredLetterOnly:
            match = True
        elif player['universalName'] == undoPlayerCommaReversal:
            match = True
        elif removeAllNonLettersAndLowercase(player['nameWithComma']) == playerLoweredLetterOnly:
            match = True
        elif player['fullName'] == playerInUnknownFormat + " Jr.":
            match = True
        elif player['fullName'] == playerInUnknownFormat + " Jnr":
            match = True
        elif player['fullName'] == playerInUnknownFormat + " Sr.":
            match = True
        elif player['fullName'] == playerInUnknownFormat + " III":
            match = True
        elif player['fullName'] == playerInUnknownFormat + " IV":
            match = True
        elif player['fullName'] + " Jr." == playerInUnknownFormat:
            match = True
        elif player['fullName'] + " Jnr" == playerInUnknownFormat:
            match = True
        elif player['fullName'] + " Sr." == playerInUnknownFormat:
            match = True
        elif player['fullName'] + " III" == playerInUnknownFormat:
            match = True
        elif player['fullName'] + " IV" == playerInUnknownFormat:
            match = True

        try:
            if removeAllNonLettersAndLowercase(player['alternateNames'][0]) == undoPlayerCommaReversal:
                match = True
        except:
            pass
        if match:
            break

    if not match:
        # raise ValueError("player", playerInUnknownFormat, "did not have a match")
        print("player", playerInUnknownFormat, "did not have a match, things may break")
        return playerInUnknownFormat

    if bballRefName:
        return player['bballRefCode']
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
        elif len(splitTeamList[-1]) > 3 and splitTeamList[-1] in team['teamName']: # make sure it's not a short code before looking in
            match = True
        elif team['simpleName'] == teamInUnknownFormat:
            match = True
        elif team['location'] == teamInUnknownFormat:
            match = True
        elif teamInUnknownFormat in team['alternateAbbreviations']:
            match = True
        elif team['abbreviation'] == teamInUnknownFormat:
            match = True
        elif team['bovadaId'] == teamInUnknownFormat:
            match = True
        if match:
            break
    # Often format is "LA Clippers" or "DEN Nuggets" or "Nuggets"

    if not match:
        raise ValueError("team", teamInUnknownFormat, "did not have a match")
    return team['abbreviation']

def getTeamIDFromShortCode(shortCode: str):
    shortCode = convertBballRefTeamShortCodeToNBA(shortCode)
    nbaTeams = teams.get_teams()
    teamDict = [team for team in nbaTeams if team['abbreviation'] == shortCode][0]
    return teamDict['id']

def _getGameObjFromDateAndTeamUsingLocalData(dateStr: str, shortCode: str):
    filePath = ENVIRONMENT.GAME_SUMMARY_UNFORMATTED_PATH
    filePath = filePath.format(shortCode)
    gameData = pd.read_csv(filePath)
    return gameData[gameData['GAME_DATE'] == dateStr]

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
    if shortCode == 'CHO' or shortCode == 'CHH':
        return 'CHA'
    if shortCode == 'NJN':
        print('dangerous return of NJN == BKN')
        return 'BKN'
    if shortCode == 'SEA':
        print('dangerous return of SEA == OKC')
        return 'OKC'
    if shortCode == 'VAN':
        print('dangerous return of VAN == MEM')
        return 'MEM'
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

def getPlayerTeamInSeasonFromBballRefLink(playerLink, season, longCode=True, returnCurrentTeam=False):
    if longCode:
        playerLink = playerLink[11:]

    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as teamPairs:
        seasons = json.load(teamPairs)
        try:
            if returnCurrentTeam:
                return seasons[str(season)][playerLink]['currentTeam']
            return seasons[str(season)][playerLink]['possibleTeams']
        except:
            raise ValueError("no match found for player", playerLink)

def getAllGamesForTeam(team_id: str):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    return gamefinder.get_data_frames()[0]

# game date format is YYYY-MM-DD
def _getGameObjFromDateAndTeam(dateStr: str, shortCode: str):
    teamId = getTeamIDFromShortCode(shortCode)
    allGames = getAllGamesForTeam(teamId)
    return allGames[allGames.GAME_DATE == str(dateStr)]
