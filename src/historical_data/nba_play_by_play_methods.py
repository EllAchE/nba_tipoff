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
import re

import requests
from nba_api.stats.endpoints import gamerotation, playbyplayv2
from typing import Any
import pandas as pd

import ENVIRONMENT
from src.database.database_access import findPlayerFullFromLastGivenPossibleFullNames, getGameIdFromBballRef, \
    getTeamDictionaryFromShortCode, getAllGamesForTeam, \
    getGameIdByTeamAndDateFromStaticData, getUniversalPlayerName, getUniversalTeamShortCode
from src.utils import sleepChecker

# backlogTodo different sites may only look at first field goal (NOT FREE THROW) which makes for a weaker correlation
# backlogTODO: Writing type stubs for pandas' DataFrame is too cumbersome, so we use this instead.
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

def saveAllHistoricalStarters():
    stub = ENVIRONMENT.GAME_SUMMARY_UNFORMATTED_PATH
    for shortCode in ENVIRONMENT.CURRENT_TEAMS:
        path = stub.format(shortCode)
        allGamesDf = pd.read_csv(path)
        allGamesDf['homeStarter1'] = None
        allGamesDf['homeStarter2'] = None
        allGamesDf['homeStarter3'] = None
        allGamesDf['homeStarter4'] = None
        allGamesDf['homeStarter5'] = None
        allGamesDf['awayStarter1'] = None
        allGamesDf['awayStarter2'] = None
        allGamesDf['awayStarter3'] = None
        allGamesDf['awayStarter4'] = None
        allGamesDf['awayStarter5'] = None
        i = 0

        while allGamesDf.iloc[i]['SEASON_ID'] != 22012:
            print("iteration", i, "for team", shortCode)
            sleepChecker(baseTime=0, randomMultiplier=1, iterations=4)
            row = allGamesDf.iloc[i]
            try:
                homeTeam, homeStarters, awayTeam, awayStarters = getSingleGameStarters(row['GAME_ID'])
                allGamesDf.at[i, 'homeStarter1'] = homeStarters[0]
                allGamesDf.at[i, 'homeStarter2'] = homeStarters[1]
                allGamesDf.at[i, 'homeStarter3'] = homeStarters[2]
                allGamesDf.at[i, 'homeStarter4'] = homeStarters[3]
                allGamesDf.at[i, 'homeStarter5'] = homeStarters[4]
                allGamesDf.at[i, 'awayStarter1'] = awayStarters[0]
                allGamesDf.at[i, 'awayStarter2'] = awayStarters[1]
                allGamesDf.at[i, 'awayStarter3'] = awayStarters[2]
                allGamesDf.at[i, 'awayStarter4'] = awayStarters[3]
                allGamesDf.at[i, 'awayStarter5'] = awayStarters[4]
            except:
                print('some error occured, values will stay as None')
            i += 1
        allGamesDf.to_csv(path, index=False)

def getSingleGameStarters(gameId):
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/gamerotation.md
    # this endpoint should provide the data
    # https://stats.nba.com/stats/gamerotation?GameID=0022000524&LeagueID=00
    headers = {
        "x-nba-stats-token":"true",
        "x-nba-stats-origin":"stats",
        "Origin":"https://nba.com",
        "Referer":"https://nba.com/",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    }
    urlStub = 'https://stats.nba.com/stats/gamerotation?GameID={}&LeagueID=00'
    url = urlStub.format('00' + str(gameId))

    response = requests.get(url, headers=headers).json()

    homeStartersSet = set()
    awayStartersSet = set()
    if response['resultSets'][0]['name'] == "AwayTeam":
        awayTeamObj = response['resultSets'][0]
        homeTeamObj = response['resultSets'][1]
    else:
        awayTeamObj = response['resultSets'][1]
        homeTeamObj = response['resultSets'][0]

    homeTeam = getUniversalTeamShortCode(homeTeamObj['rowSet'][0][2] + ' ' + homeTeamObj['rowSet'][0][3])
    awayTeam = getUniversalTeamShortCode(awayTeamObj['rowSet'][0][2] + ' ' + awayTeamObj['rowSet'][0][3])

    for playerInOut in homeTeamObj['rowSet']:
        if playerInOut[-5] == 0.0:
            name = playerInOut[5] + ' ' + playerInOut[6]
            homeStartersSet.add(getUniversalPlayerName(name))
    for playerInOut in awayTeamObj['rowSet']:
        if playerInOut[-5] == 0.0:
            name = playerInOut[5] + ' ' + playerInOut[6]
            awayStartersSet.add(getUniversalPlayerName(name))

    homeStarters = list()
    awayStarters = list()
    for item in homeStartersSet:
        homeStarters.append(item)
    for item in awayStartersSet:
        awayStarters.append(item)

    return homeTeam, homeStarters, awayTeam, awayStarters

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

def getFirstScoreLine(gameCode, season):
    with open("Data/JSON/Public_NBA_API/shots_before_first_field_goal") as sbffg:
        firstScoreDict = json.load(sbffg)
    return firstScoreDict[season][gameCode]

def parseDataFromTipoffLine(tipoffContent, type, isHome):
    print(tipoffContent)
    # tipper1 = getBballRefPlayerName(None)
    #tipper2 = getBballRefPlayerName(None)
    #possessingPlayer = getBballRefPlayerName(None)
    homeTipper = None
    awayTipper = None
    firstScoret = None
    tipWinningTeam = None
    tipLosingTeam = None
    possessingTeam = None
    firstScoringTeam = None
    scoredUponTeam = None
    tipoffWinner = None
    tipoffLoser = None
    tipLoserLink = None
    tipWinnerlink = None
    tipWinnerScores = None

def getTipoffLineFromBballRefId(bballRef: str):
    gameId = getGameIdFromBballRef(bballRef)
    pbpDf = getGamePlayByPlay(gameId)
    tipoffContent, type, isHome = getTipoffLine(pbpDf)
    parseDataFromTipoffLine(tipoffContent, type, isHome)
    return tipoffContent, type, isHome

def splitAllSeasonsFirstShotDataToMultipleFiles():
    with open(ENVIRONMENT.ALL_SHOTS_BEFORE_FIRST_FG_PATH) as allDataFile:
        allDataDict = json.load(allDataFile)

    stub = ENVIRONMENT.SINGLE_SEASON_SHOTS_BEFORE_FIRST_FG_PATH
    data2014 = allDataDict['2014']
    data2015 = allDataDict['2015']
    data2016 = allDataDict['2016']
    data2017 = allDataDict['2017']
    data2018 = allDataDict['2018']
    data2019 = allDataDict['2019']
    data2020 = allDataDict['2020']
    data2021 = allDataDict['2021']

    with open(stub.format('2014'), 'w') as f2014:
        json.dump(data2014, f2014, indent=4)

    with open(stub.format('2015'), 'w') as f2015:
        json.dump(data2015, f2015, indent=4)

    with open(stub.format('2016'), 'w') as f2016:
        json.dump(data2016, f2016, indent=4)

    with open(stub.format('2017'), 'w') as f2017:
        json.dump(data2017, f2017, indent=4)

    with open(stub.format('2018'), 'w') as f2018:
        json.dump(data2018, f2018, indent=4)

    with open(stub.format('2019'), 'w') as f2019:
        json.dump(data2019, f2019, indent=4)

    with open(stub.format('2020'), 'w') as f2020:
        json.dump(data2020, f2020, indent=4)

    with open(stub.format('2021'), 'w') as f2021:
        json.dump(data2021, f2021, indent=4)

# backlogtodo fix this to not break for some specific players and . names, i.e. Nene or W. or Shaw.
def getAllFirstPossessionStatisticsIncrementally(season):
    path = ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH
    path = path.format(season)
    df = pd.read_csv(path)
    i = 0
    dfLen = len(df.index)

    with open(ENVIRONMENT.ALL_SHOTS_BEFORE_FIRST_FG_PATH) as sbfs:
        shotsDict = json.load(sbfs)
    seasonShotList = shotsDict[str(season)]

    if len(seasonShotList) > 0:
        lastGame = seasonShotList[-1]
        lastGameCode = lastGame['gameCode']
        lastGameIndex = df[df['Game Code'] == lastGameCode].index.values[0]
        i = lastGameIndex + 1
        # backlogtodo figure out why some of these games are breaking. In fetching the data a small number of games were ignored due to failure to return data
    while i < dfLen:
        with open(ENVIRONMENT.ALL_SHOTS_BEFORE_FIRST_FG_PATH) as sbfs:
            shotsDict = json.load(sbfs)
        seasonShotList = shotsDict[str(season)]

        bballRefId = df.iloc[i]["Game Code"]
        print('running for ', bballRefId)
        # gameId = getGameIdFromBballRef(bballRefId)
        gameId = '00' + str(getGameIdByTeamAndDateFromStaticData(bballRefId))
        q1Shots, q2Shots, q3Shots, q4Shots = gameIdToFirstFieldGoalsOfQuarters(gameId)
        gameStatistics = _getFirstShotStatistics(q1Shots, q2Shots, q3Shots, q4Shots, bballRefId)
        seasonShotList.append(gameStatistics)
        sleepChecker(iterations=1, baseTime=10, randomMultiplier=1)

        shotsDict[str(season)] = seasonShotList
        with open(ENVIRONMENT.ALL_SHOTS_BEFORE_FIRST_FG_PATH, 'w') as jsonFile:
            json.dump(shotsDict, jsonFile, indent=4)

        i += 1

def fillGapsLooper():
    for year in ENVIRONMENT.ALL_SEASONS_LIST:
        pathIn = ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(year) #ENVIRONMENT.SEASON_DATA_GAPS
        pathOut = (ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH[:-4] + "_{}.csv").format(year, "no_gaps") #ENVIRONMENT.SEASON_DATA_GAPS_FILLED
        print("run for ", year, pathIn, pathOut)
        fillGaps(year, pathIn, pathOut)


def fillGaps(season, pathIn, pathOut):
    fin = open(pathIn, 'r', encoding='utf8')
    #fout = open(pathOut, 'w')
    fout = open('test.txt', 'w', encoding='utf8')
    count = 0
    for line in fin:
        if re.search(',,,,,,,,,,,,', line) is not None:
            tokenized = line.split(',')
            gameCode = tokenized[0]
            #fout.write(str(count) + ', ' + str(tokenized[0]) + ', ' + str(year) + ', ' + str(tokenized[4]) + ', ' + str(tokenized[5]))
            fout.write(str(count) + ': ' + line)
            try:
                tipOffContent, type, isHome = getTipoffLineFromBballRefId(gameCode)
                fout.write(tipOffContent)
            except IndexError:
                fout.write("failed to retrieve for " + gameCode)
            count += 1

            print(count)
            sleepChecker(1, 10, 1, True)
            #print(nba_public.getParticipatingTeamsFromId(nba_public.getGameIdFromBballRef(gameCode)))
        #else:
            #fout.write(line)
            #print(line)
    fin.close()
    fout.close()

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

# todo fill in the blanks on the missing games in the csv
