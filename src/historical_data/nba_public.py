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

import ENVIRONMENT
from src.functions.database_access import findPlayerFullFromLastGivenPossibleFullNames, getGameIdFromBballRef, \
    getTeamDictionaryFromShortCode, getAllGamesForTeam
from src.functions.utils import getDashDateAndHomeCodeFromGameCode, sleepChecker

# Todo different sites may only look at first field goal (NOT FREE THROW) which makes for a much weaker correlation
# TODO: Writing type stubs for pandas' DataFrame is too cumbersome, so we use this instead.
# Eventually, we should replace that with real type stubs for DataFrame.
DataFrame = Any

def getAllGamesInSeason(season: int, short_code: str):
    season -= 1
    teamId = getTeamDictionaryFromShortCode(short_code)
    gamesDf = getAllGamesForTeam(teamId)
    
    return gamesDf[gamesDf.SEASON_ID.str[-4:] == str(season)]

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

def _getSingleQuarterStatistics(shotsBeforeFirstScore: pd.DataFrame):
    dataList = list()
    gameId = shotsBeforeFirstScore.iloc[0].GAME_ID
    teamDict = getParticipatingTeamsFromId(gameId)
    allGamePlayers = getGamePlayersFromId(gameId)
    homeTeam = teamDict['home']
    awayTeam = teamDict['away']

    shotIndex = 0
    for abc in shotsBeforeFirstScore.EVENTNUM:
        row = shotsBeforeFirstScore.iloc[shotIndex]
        description = row.HOMEDESCRIPTION if row.HOMEDESCRIPTION is not None else row.VISITORDESCRIPTION
        playerTeam = awayTeam if row.HOMEDESCRIPTION is None else homeTeam
        playerLast = getPlayerLastNameFromShotDescription(description)
        player = findPlayerFullFromLastGivenPossibleFullNames(playerLast, allGamePlayers)
        shotType = getShotTypeFromEventDescription(description)
        if playerTeam == homeTeam:
            opponentTeam = awayTeam
        else:
            opponentTeam = homeTeam

        dataList.append({"shotIndex": shotIndex, "team": playerTeam, "player": player, "opponentTeam": opponentTeam, "shotType": shotType}) # free throws should be considered a collective shot, not individual
        shotIndex += 1
    return dataList

def _getFirstShotStatistics(q1Shots: pd.DataFrame, q2Shots: pd.DataFrame, q3Shots: pd.DataFrame, q4Shots: pd.DataFrame, bballRefCode: str):
    q1Stats = _getSingleQuarterStatistics(q1Shots)
    q2Stats = _getSingleQuarterStatistics(q2Shots)
    q3Stats = _getSingleQuarterStatistics(q3Shots)
    q4Stats = _getSingleQuarterStatistics(q4Shots)
    return {"gameCode": bballRefCode, "quarter1": q1Stats, "quarter2": q2Stats, "quarter3": q3Stats, "quarter4": q4Stats}

def _getFirstQuarterShotStatistics(shotsBeforeFirstScore: pd.DataFrame, bballRefCode: str):
    dataList = _getSingleQuarterStatistics(shotsBeforeFirstScore)
    return {"gameCode": bballRefCode, "gameData": dataList}

def _getAllShotsBeforeFirstFieldGoal(playsBeforeFirstFgDf: DataFrame):
    shootingPlays = playsBeforeFirstFgDf[playsBeforeFirstFgDf['EVENTMSGTYPE'].isin([1, 2, 3])]
    return shootingPlays

def getEventsBeforeFirstFieldGoalOfQuarter(pbpDf: DataFrame, startIndex: int=0):
    startIndex += 1
    i = 0
    pbpDf = pbpDf[startIndex:]
    for item in pbpDf.SCORE:
        eventMsgType = pbpDf.iloc[i]['EVENTMSGTYPE']
        if item is not None and (eventMsgType == 2 or eventMsgType == 1):
            return pbpDf[:(i + 1)]
        i += 1

def gameIdToFirstFieldGoalsOfQuarters(id: str):
    pbpDf = playbyplayv2.PlayByPlayV2(game_id=id).get_data_frames()[0]
    indicesOfQuarterStarts = pbpDf.index[pbpDf['EVENTMSGTYPE'] == 12].tolist()
    q2Index = indicesOfQuarterStarts[1]
    q3Index = indicesOfQuarterStarts[2]
    q4Index = indicesOfQuarterStarts[3]

    plays = getEventsBeforeFirstFieldGoalOfQuarter(pbpDf)
    q1Shots = _getAllShotsBeforeFirstFieldGoal(plays)

    plays = getEventsBeforeFirstFieldGoalOfQuarter(pbpDf, q2Index)
    q2Shots = _getAllShotsBeforeFirstFieldGoal(plays)

    plays = getEventsBeforeFirstFieldGoalOfQuarter(pbpDf, q3Index)
    q3Shots = _getAllShotsBeforeFirstFieldGoal(plays)

    plays = getEventsBeforeFirstFieldGoalOfQuarter(pbpDf, q4Index)
    q4Shots = _getAllShotsBeforeFirstFieldGoal(plays)

    return q1Shots, q2Shots, q3Shots, q4Shots

def gameIdToFirstShotList(id: str):
    pbpDf = playbyplayv2.PlayByPlayV2(game_id=id).get_data_frames()[0]
    plays = getEventsBeforeFirstFieldGoalOfQuarter(pbpDf)
    shots = _getAllShotsBeforeFirstFieldGoal(plays)
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

def getTipoffLineFromBballRefId(bballRef: str):
    gameId = getGameIdFromBballRef(bballRef)
    pbpDf = getGamePlayByPlay(gameId)
    tipoffContent, type, isHome = getTipoffLine(pbpDf)
    return tipoffContent

# todo fix this to not break for some specific players and . names, i.e. Nene or W. or Shaw.
def getAllFirstPossessionStatisticsIncrementally(season):
    path = 'Data/CSV/tipoff_and_first_score_details_{}_season.csv'.format(season)
    df = pd.read_csv(path)
    i = 0
    dfLen = len(df.index)

    with open('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json') as sbfs:
        shotsDict = json.load(sbfs)
    seasonShotList = shotsDict[str(season)]

    if len(seasonShotList) > 0:
        lastGame = seasonShotList[-1]
        lastGameCode = lastGame['gameCode']
        lastGameIndex = df[df['Game Code'] == lastGameCode].index.values[0]
        i = lastGameIndex + 1
    while i < dfLen:
        with open('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json') as sbfs:
            shotsDict = json.load(sbfs)
        seasonShotList = shotsDict[str(season)]

        bballRefId = df.iloc[i]["Game Code"]
        print('running for ', bballRefId)
        gameId = getGameIdFromBballRef(bballRefId)
        q1Shots, q2Shots, q3Shots, q4Shots = gameIdToFirstFieldGoalsOfQuarters(gameId)
        gameStatistics = _getFirstShotStatistics(q1Shots, q2Shots, q3Shots, q4Shots, bballRefId)
        seasonShotList.append(gameStatistics)
        sleepChecker(iterations=1, baseTime=10, randomMultiplier=1)

        shotsDict[str(season)] = seasonShotList
        with open('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json', 'w') as jsonFile:
            json.dump(shotsDict, jsonFile)

        i += 1

# def getAllFirstQuarterFirstPossessionStatisticsIncrementally(season):
#     path = 'Data/CSV/tipoff_and_first_score_details_{}_season.csv'.format(season)
#     df = pd.read_csv(path)
#     i = 0
#     dfLen = len(df.index)
#
#     with open('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json') as sbfs:
#         shotsDict = json.load(sbfs)
#     seasonShotList = shotsDict[str(season)]
#
#     if len(seasonShotList) > 0:
#         lastGame = seasonShotList[-1]
#         lastGameCode = lastGame['gameCode']
#         lastGameIndex = df[df['Game Code'] == lastGameCode].index.values[0]
#         i = lastGameIndex + 1
#     while i < dfLen:
#         with open('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json') as sbfs:
#             shotsDict = json.load(sbfs)
#         seasonShotList = shotsDict[str(season)]
#
#         bballRefId = df.iloc[i]["Game Code"]
#         print('running for ', bballRefId)
#         gameId = getGameIdFromBballRef(bballRefId)
#         gameShots = gameIdToFirstShotList(gameId)
#         gameStatistics = _getFirstQuarterShotStatistics(gameShots, bballRefId)
#         seasonShotList.append(gameStatistics)
#         sleepChecker(iterations=3, baseTime=0, randomMultiplier=1)
#
#         shotsDict[str(season)] = seasonShotList
#         with open('Data/JSON/Public_NBA_API/shots_before_first_field_goal.json', 'w') as jsonFile:
#             json.dump(shotsDict, jsonFile)
#
#         i += 1

# test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'], ['199711160SEA', 'SEA', 'MIL'], ['199711190LAL', 'LAL', 'MIN'],
#   ['201911200TOR', 'TOR', 'ORL'], ['201911260DAL', 'DAL', 'LAC']] # Last one is a violation, others are misformatted

# class EventMsgType(Enum):
#     FIELD_GOAL_MADE = 1 #backlogtodo replace above uses of numbers with ENUM values for readability
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
