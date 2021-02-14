# Finding Games
# https://github.com/swar/nba_api/blob/master/docs/examples/Finding%20Games.ipynb

# Pulling play by play
# https://github.com/swar/nba_api/blob/master/docs/examples/PlayByPlay.ipynb

'''
1. Individual player scoring percent on first shot
2. player score percent overall
3. Team score percent first shot
4. Team score percent overall
5. The above but for defense (opponents)
6. Percentage of first shots taken by particular player
7. Percentage of first shots made by player overall
8. Above two extended up until first basket made/for first X shots
9. Above for opponents
10. Team FT rate, two point vs. 3 point etc.
11. Number of shots until first made
12. First tip performance
13. Non standard tip
14. Low appearance tip

To fetch here
Individual player scoring percent on first shot
Team score percent first shot
Percentage of first shots made by player overall
Percentage of first shots taken by particular player

'''
import json

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import gamerotation, playbyplayv2
from typing import Any
import pandas as pd
from nba_api.stats.static import players

# TODO: Writing type stubs for pandas' DataFrame is too cumbersome, so we use this instead.
# Eventually, we should replace that with real type stubs for DataFrame.
import ENVIRONMENT
from tipoff.functions.utils import getDashDateAndHomeCodeFromGameCode, sleepChecker

DataFrame = Any

def convertBballRefTeamShortCodeToNBA(shortCode: str):
    if shortCode == 'PHO':
        return 'PHX'
    if shortCode == 'BRK':
        return 'BKN'
    if shortCode == 'CHO':
        return 'CHA'
    return shortCode

def getTeamDictionaryFromShortCode(shortCode: str):
    shortCode = convertBballRefTeamShortCodeToNBA(shortCode)
    nbaTeams = teams.get_teams()
    teamDict = [team for team in nbaTeams if team['abbreviation'] == shortCode][0]
    return teamDict['id']

def getAllGamesForTeam(team_id: str):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    return gamefinder.get_data_frames()[0]

def getAllGamesInSeason(season: int, short_code: str):
    season -= 1
    teamId = getTeamDictionaryFromShortCode(short_code)
    gamesDf = getAllGamesForTeam(teamId)
    
    return gamesDf[gamesDf.SEASON_ID.str[-4:] == str(season)]

# game date format is YYYY-MM-DD
def _getGameObjFromDateAndTeam(dateStr: str, shortCode: str):
    teamId = getTeamDictionaryFromShortCode(shortCode)
    allGames = getAllGamesForTeam(teamId)
    return allGames[allGames.GAME_DATE == str(dateStr)]

def getGameIdFromTeamAndDate(dateStr: str, shortCode: str):
    gameObj = _getGameObjFromDateAndTeam(dateStr, shortCode)
    return gameObj.GAME_ID.iloc[0]

def getGamePlayByPlay(gameId: str):
    return playbyplayv2.PlayByPlayV2(gameId).get_data_frames()[0]

def getPlayerLastNameFromShotDescription(description: str): # if this need to be fully generic then fetch the playerlast names and do a match on that
    isMiss = "MISS" in description
    splitDescription = description.split(' ')
    
    if isMiss:
        return splitDescription[1]
    else:
        return splitDescription[0]

def getShotTypeFromEventDescription(description: str):
    isMiss = "MISS" if "MISS" in description or "BLOCK" in description else "MAKE"
    
    if "3PT" in description:
        return "3PT " + isMiss
    
    if "Free Throw" in description:
        return "FREE THROW " + isMiss
    
    return "2PT " + isMiss

def findPlayerFullFromLast(playerLastName, playerList):
    for player in playerList:
        if playerLastName == player["lastName"]:
            return player["fullName"]
    print('couldn\'t match player' + playerLastName)
    return playerLastName

def _getFirstShotStatistics(shotsBeforeFirstScore: pd.DataFrame, bballRefCode):
    shotIndex = 0
    dataList = list()
    gameId = shotsBeforeFirstScore.iloc[0].GAME_ID
    teamDict = getParticipatingTeamsFromId(gameId)
    allGamePlayers = getGamePlayersFromId(gameId)
    homeTeam = teamDict['home']
    awayTeam = teamDict['away']

    dfLen = len(shotsBeforeFirstScore.index)
    while shotIndex < dfLen:
        row = shotsBeforeFirstScore.iloc[shotIndex]
        description = row.HOMEDESCRIPTION if row.HOMEDESCRIPTION is not None else row.VISITORDESCRIPTION
        playerTeam = awayTeam if row.HOMEDESCRIPTION is None else homeTeam
        playerLast = getPlayerLastNameFromShotDescription(description)
        player = findPlayerFullFromLast(playerLast, allGamePlayers)
        shotType = getShotTypeFromEventDescription(description)
        if playerTeam == homeTeam:
            opponentTeam = awayTeam
        else:
            opponentTeam = homeTeam

        dataList.append({"shotIndex": shotIndex, "team": playerTeam, "player": player, "opponentTeam": opponentTeam, "shotType": shotType}) # free throws should be considered a collective shot, not individual
        shotIndex += 1
        # todo map the player lastName retrieved here to a player index/code
    return {"gameCode": bballRefCode, "gameData": dataList}

def _getAllShotsBeforeFirstScore(playsBeforeFirstFgDf: DataFrame):
    shootingPlays = playsBeforeFirstFgDf[playsBeforeFirstFgDf['EVENTMSGTYPE'].isin([1, 2, 3])]
    return shootingPlays

def getAllEventsBeforeFirstScore(pbpDf: DataFrame):
    i = 0
    for item in pbpDf.SCORE:
        if item is not None:
            return pbpDf[:(i + 1)]
        i += 1

def gameIdToFirstShotList(id: str):
    pbpDf = playbyplayv2.PlayByPlayV2(game_id=id).get_data_frames()[0]
    plays = getAllEventsBeforeFirstScore(pbpDf)
    shots = _getAllShotsBeforeFirstScore(plays)

    return shots

def getParticipatingTeamsFromId(id): # (id: str) -> dict[str, str]:
    response = gamerotation.GameRotation(game_id=id)
    awayTeamCity = response.away_team.get_dict()['data'][0][2]
    awayTeamName = response.away_team.get_dict()['data'][0][3]
    awayTeamId = response.away_team.get_dict()['data'][0][4]
    homeTeamCity = response.home_team.get_dict()['data'][0][2]
    homeTeamName = response.home_team.get_dict()['data'][0][3]
    homeTeamId = response.home_team.get_dict()['data'][0][4]
    
    return {"home": homeTeamCity + ' ' + homeTeamName, "homeId": homeTeamId, "away": awayTeamCity + ' ' + awayTeamName, "awayId": awayTeamId}

def getGamePlayersFromId(id):
    playerSet = set()
    playerList = list()
    response = gamerotation.GameRotation(game_id=id)
    rotation1, rotation2 = response.get_data_frames()
    allRotations = pd.concat([rotation1, rotation2])
    i = 0
    dfLen = len(allRotations.index)
    while i < dfLen:
        last = allRotations.iloc[i].PLAYER_LAST
        playerFull = allRotations.iloc[i].PLAYER_FIRST + ' ' + last
        playerSet.add(playerFull)
        i += 1

    for player in playerSet:
        lastName = player.split(' ')
        playerList.append({"fullName": player, "lastName": lastName[1]})

    return playerList

def getTipoffLine(pbpDf: DataFrame, returnIndex: bool = False):
    try:
        tipoffSeries = pbpDf[pbpDf.EVENTMSGTYPE == 10]
        tipoffContent = tipoffSeries.iloc[0]
        type = 10
    except:
        tipoffSeries = pbpDf[pbpDf.EVENTMSGTYPE == 7]
        tipoffContent = tipoffSeries.iloc[0]
        type = 7

    print('Home Desc', tipoffContent.HOMEDESCRIPTION, 'Vis Desc', tipoffContent.VISITORDESCRIPTION, 'Neut Desc', tipoffContent.NEUTRALDESCRIPTION)

    if tipoffContent.HOMEDESCRIPTION is not None:
        content = tipoffContent.HOMEDESCRIPTION
        isHome = True
    elif tipoffContent.VISITORDESCRIPTION is not None:
        content = tipoffContent.VISITORDESCRIPTION
        isHome = False
    else:
        raise ValueError('nothing for home or away, neutral said', tipoffContent.NEUTRALDESCRIPTION)

    if returnIndex:
        return content, type, isHome, tipoffContent.index
    return content, type, isHome

def getTipoffLineFromGameId(gameId: str):
    pbpDf = getGamePlayByPlay(gameId)
    tipoffContent = getTipoffLine(pbpDf)
    return tipoffContent

def getGameIdFromBballRef(bballRefId):
    date, team = getDashDateAndHomeCodeFromGameCode(bballRefId)
    return getGameIdFromTeamAndDate(date, team)

def getAllFirstPossessionStatisticsIncrementally(season):
    path = '../../Data/CSV/tipoff_and_first_score_details_{}_season.csv'.format(season)
    df = pd.read_csv(path)
    i = 0
    sleepCounter = 0
    dfLen = len(df.index)

    with open('../../Data/JSON/Public_NBA_API/shots_before_first_score.json') as sbfs:
        shotsDict = json.load(sbfs)
    seasonShotList = shotsDict[str(season)]

    if len(seasonShotList) > 0:
        lastGame = seasonShotList[-1]
        lastGameCode = lastGame['gameCode']
        lastGameIndex = df[df['Game Code'] == lastGameCode].index.values[0]
        i = lastGameIndex + 1
    while i < dfLen:
        with open('../../Data/JSON/Public_NBA_API/shots_before_first_score.json') as sbfs:
            shotsDict = json.load(sbfs)
        seasonShotList = shotsDict[str(season)]

        bballRefId = df.iloc[i]["Game Code"]
        print('running for ', bballRefId)
        gameId = getGameIdFromBballRef(bballRefId)
        gameShots = gameIdToFirstShotList(gameId)
        gameStatistics = _getFirstShotStatistics(gameShots, bballRefId)
        seasonShotList.append(gameStatistics)
        sleepChecker(sleepCounter, iterations=3, baseTime=0, randomMultiplier=1)

        shotsDict[str(season)] = seasonShotList
        with open('../../Data/JSON/Public_NBA_API/shots_before_first_score.json', 'w') as jsonFile:
            json.dump(shotsDict, jsonFile)

        i += 1
#
#
# def getPlayerIdFromFullName(name):
#     nba_players = players.get_players()
#     playerObj = [player for player in nba_players if player['full_name'] == name][0]
#     id = playerObj.id
#     return id

def getAllFirstPossessionStatisticsAtOnce():
    allShotsList = list()
    for season in ENVIRONMENT.SEASONS_LIST_SINCE_HORNETS:
        path = '../../Data/CSV/tipoff_and_first_score_details_{}_season.csv'.format(season)
        df = pd.read_csv(path)
        i = 0
        sleepCounter = 0
        dfLen = len(df.index)
        seasonShotList = list()

        while i < dfLen:
            bballRefId = df.iloc[i]["Game Code"]
            print('running for ', bballRefId)
            gameId = getGameIdFromBballRef(bballRefId)
            gameShots = gameIdToFirstShotList(gameId)
            gameStatistics = _getFirstShotStatistics(gameShots, bballRefId)
            seasonShotList.append(gameStatistics)
            sleepChecker(sleepCounter, iterations=1, baseTime=2, randomMultiplier=2)
            i += 1

        temp = {"season": season, "games": seasonShotList}
        allShotsList.append(temp)

    with open(ENVIRONMENT.SHOTS_BEFORE_FIRST_SCORE_PATH, 'w') as jsonFile:
        json.dump(allShotsList, jsonFile)

# class EventMsgType(Enum):
#     FIELD_GOAL_MADE = 1 #todo replace above uses of numbers with ENUM values for readability
#     FIELD_GOAL_MISSED = 2
#     FREE_THROWfree_throw_attempt = 3
#     REBOUND = 4
#     TURNOVER = 5
#     FOUL = 6
#     VIOLATION = 7
#     SUBSTITUTION = 8
#     TIMEOUT = 9
#     JUMP_BALL = 10
#     EJECTION = 11
#     PERIOD_BEGIN = 12
#     PERIOD_END = 13

# def getNbaComResultsFromBballReferenceCode(bballCode):
#     date, team_code = getDashDateAndHomeCodeFromGameCode(bballCode)
#     test = getGameIdFromTeamAndDate(date, team_code)
#     deb = getTipoffResults(test)
#     print(deb)

# todo use this work (specifically the getTipoffLine) to fill in the blanks on the missing games in the csv
