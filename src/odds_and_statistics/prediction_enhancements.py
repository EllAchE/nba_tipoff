# backlogtodo offensive rebounding/defensive rebounding influence
# backlogtodo add other stats and run ludwig/ai checker
import pandas as pd
import json
from collections import OrderedDict
import requests
import ENVIRONMENT
from src.database.database_access import getUniversalTeamShortCode
from src.utils import lowercaseNoSpace

# backlogtodo include nonshooting possessions
# todo these should be done:
#    Offensive efficiency, Def E, Percentage of FT & 2s vs. 3s (effective score percentage),
# backlogtodo  usage rate for players

def getCurrentSeasonUsageRate():
    headers = {
        'x-nba-stats-token':'true',
        'x-nba-stats-origin':'stats',
        'Origin':'https://nba.com',
        'Referer':'https://nba.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    }
    response = requests.get(url='https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=5&LeagueID=00&Location=&MeasureType=Usage&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight=',
                            headers=headers).json()

    playerUsageDict = response

    with open(ENVIRONMENT.PLAYER_USAGE_PATH, 'w') as pUsageFile:
        json.dump(playerUsageDict, pUsageFile)

    print('saved Player Usage Dictionary')

def getAllSeasonFirstFieldGoalOrFirstPointStats(isFirstFieldGoal=False):
    for season in ENVIRONMENT.SEASONS_SINCE_HORNETS_LIST:
        getFirstFieldGoalOrFirstPointStats(season, isFirstFieldGoal=isFirstFieldGoal)

def getFirstFieldGoalOrFirstPointStats(season, isFirstFieldGoal=False):
    stub = ENVIRONMENT.SINGLE_SEASON_SHOTS_BEFORE_FIRST_FG_PATH
    with open(stub.format(season)) as data:
        firstShotsDict = json.load(data)

    summaryDict = {}

    # summaryDict = _initializePlayerDict(summaryDict, firstShotsDict)
    summaryDict = _initializeTeamDict(summaryDict, firstShotsDict)
    seasonData = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season))

    for game in firstShotsDict:
        # summaryDict = _playerFirstShotStats(game, summaryDict, isFirstFieldGoal=isFirstFieldGoal)
        summaryDict = _teamFirstShotStats(game, summaryDict, seasonData, isFirstFieldGoal=isFirstFieldGoal)

    summaryDict = _summaryStats(summaryDict)

    def sortFunction(item):
        quarterData = list(item)[1]['quarter1']
        return quarterData['2PT MAKE'] + quarterData['3PT MAKE']

    summaryDict = OrderedDict(sorted(summaryDict.items(), key=sortFunction, reverse=True))
    savePath = ENVIRONMENT.FIRST_FG_SUMMARY_UNFORMATTED_PATH.format(str(season)) if isFirstFieldGoal else ENVIRONMENT.FIRST_POINT_SUMMARY_UNFORMATTED_PATH.format(str(season))

    with open(savePath, 'w') as writeFile:
        json.dump(summaryDict, writeFile, indent=4)
    print('first shot statistics compiled. Total makes was counted as?')

def _initializePlayerDict(summaryDict, lastSeasonData):
    playerSet = set()
    quarters = ['quarter1']#, 'quarter2', 'quarter3', 'quarter4']
    # currently only looking at q1 for players
    for game in lastSeasonData:
        for quarter in quarters:
            for event in game[quarter]:
                playerSet.add(event['player'])

    for player in playerSet:
        summaryDict[player] = {}
    for player in playerSet:
        for quarter in quarters:
            summaryDict[player][quarter] = {'2PT MAKE': 0, '3PT MAKE': 0, 'FREE THROW MAKE': 0, 'FG ATTEMPTS': 0,
                                            '2PT MISS': 0, '3PT MISS': 0, 'FREE THROW MISS': 0, 'FREE THROW ATTEMPTS': 0,
                                            'firstShotIndex': 0, 'firstShots': 0, 'averageShotIndex': 0, 'gamesStarted': 0,
                                            'totalMakes': 0, 'teams': [], 'favorableTipResults': 0} # backlogtodo get games started as a separate stat
    return summaryDict

def _initializeTeamDict(summaryDict, lastSeasonData):
    teamSet = set()
    quarters = ['quarter1', 'quarter2', 'quarter3', 'quarter4']
    for game in lastSeasonData:
        for quarter in quarters:
            for event in game[quarter]:
                teamSet.add(event['team'])

    for team in teamSet:
        summaryDict[team] = {}
    for team in teamSet:
        for quarter in quarters:
            summaryDict[team][quarter] = {'favorableTipResults': 0, '2PT MAKE': 0, '3PT MAKE': 0, 'FREE THROW MAKE': 0,
                                          'FG ATTEMPTS': 0, '2PT MISS': 0, '3PT MISS': 0, 'FREE THROW MISS': 0,
                                          'FREE THROW ATTEMPTS': 0, 'opponentFgAttempts': 0, 'opponentFtAttempts': 0,
                                          'opponent2ptmake': 0, 'opponent2ptmiss': 0, 'opponent3ptmake': 0, 'opponent3ptmiss': 0,
                                          'opponentfreethrowmake': 0, 'opponentfreethrowmiss': 0}
    return summaryDict

def getTipoffResultFromGameCode(gameCode, seasonData):
    tipoffLine = seasonData.loc[seasonData['Game Code'] == gameCode].reset_index()
    win = getUniversalTeamShortCode(tipoffLine['Tip Winning Team'][0])
    lose = getUniversalTeamShortCode(tipoffLine['Tip Losing Team'][0])
    return win, lose

def _teamFirstShotStats(game, summaryDict, seasonData, isFirstFieldGoal=False):
    # todo add favorable/unfavorable tip result to quarter data
    quarters = ['quarter1', 'quarter2', 'quarter3', 'quarter4']
    try:
        tipWinTeam, tipLoseTeam = getTipoffResultFromGameCode(game['gameCode'], seasonData)
        retrievalError = False
    except:
        print('failed to get details from gameCode, may be a None line')
        retrievalError = True


    for quarter in quarters:
        isFirstTimeThrough = True
        for event in game[quarter]:
            team = event['team']
            opponent = event['opponentTeam']
            if isFirstTimeThrough:
                if not retrievalError:
                    teamWonTip = 1 if tipWinTeam == getUniversalTeamShortCode(team) else 0
                    opponentWonTip = 1 if tipWinTeam == getUniversalTeamShortCode(opponent) else 0
                else:
                    teamWonTip = 0.5
                    opponentWonTip = 0.5
                if quarter == 'quarter1' or quarter == 'quarter4':
                    summaryDict[team][quarter]["favorableTipResults"] += teamWonTip
                    summaryDict[opponent][quarter]["favorableTipResults"] += opponentWonTip
                else:
                    summaryDict[team][quarter]["favorableTipResults"] += opponentWonTip
                    summaryDict[opponent][quarter]["favorableTipResults"] += teamWonTip
                isFirstTimeThrough = False

            summaryDict[team][quarter][event['shotType']] += 1
            summaryDict[opponent][quarter][lowercaseNoSpace('opponent' + event['shotType'])] += 1

            if '2PT' in event['shotType'] or '3PT' in event['shotType']:
                summaryDict[team][quarter]['FG ATTEMPTS'] += 1
                summaryDict[opponent][quarter]['opponentFgAttempts'] += 1
            else:
                summaryDict[team][quarter]['FREE THROW ATTEMPTS'] += 1
                summaryDict[opponent][quarter]['opponentFtAttempts'] += 1
            if not isFirstFieldGoal and 'MAKE' in event['shotType']:
                break

    return summaryDict

def _summaryStats(summaryDict):
    # for playerOrTeam in summaryDict:
        # try:
        #     summaryDict[playerOrTeam]['shootingPercentage'] = (summaryDict[playerOrTeam]['2PT MAKE'] + summaryDict[playerOrTeam]['3PT MAKE'])\
        #                                                 / (summaryDict[playerOrTeam]['2PT MAKE'] + summaryDict[playerOrTeam]['3PT MAKE'] + summaryDict[playerOrTeam]['2PT MISS'] + summaryDict[playerOrTeam]['3PT MISS'])
        # except:
        #     summaryDict[playerOrTeam]['shootingPercentage'] = None
        # try:
        #     summaryDict[playerOrTeam]['freeThrowPercentage'] = (summaryDict[playerOrTeam]['FREE THROW MAKE']) / (summaryDict[playerOrTeam]['FREE THROW MAKE']  + summaryDict[playerOrTeam]['FREE THROW ATTEMPTS'])
        # except:
        #     summaryDict[playerOrTeam]['freeThrowPercentage'] = None

    return summaryDict

# backlogtodo normalize for games started, compare to known player usage rate for a given season
def _playerFirstShotStats(game, summaryDict, isFirstFieldGoal=False):
    playerHasShotInGame = set()
    quarters = ['quarter1']#, 'quarter2', 'quarter3', 'quarter4']
    # only consider first quarter shots for individual players currently

    def getTotalShots(playerQuarter):
        return playerQuarter['FG ATTEMPTS'] + playerQuarter['FREE THROW ATTEMPTS']

    def getTotalShotsDenominator(playerQuarter):
        return getTotalShots(playerQuarter) + 1

    for quarter in quarters:
        for event in game[quarter]:
            player = event['player']
            playerTeam = event['team']
            if playerTeam not in summaryDict[player][quarter]['teams']:
                summaryDict[player][quarter]['teams'].append(playerTeam)
            summaryDict[player][quarter]['averageShotIndex'] = (getTotalShots(summaryDict[player][quarter]) * summaryDict[player][quarter][
                'averageShotIndex'] + event['shotIndex']) / (getTotalShotsDenominator(summaryDict[player][quarter]))

            if player not in playerHasShotInGame:
                summaryDict[player][quarter]['firstShotIndex'] = (getTotalShots(summaryDict[player][quarter]) * summaryDict[player][quarter][
                    'firstShotIndex'] + event['shotIndex']) / (getTotalShotsDenominator(summaryDict[player][quarter]))
            playerHasShotInGame.add(player)
            summaryDict[player][quarter][event['shotType']] += 1
            if event['shotIndex'] == 1:
                summaryDict[player][quarter]['firstShots'] += 1
            if '2PT' in event['shotType'] or '3PT' in event['shotType']:
                summaryDict[player][quarter]['FG ATTEMPTS'] += 1
            else:
                summaryDict[player][quarter]['FREE THROW ATTEMPTS'] += 1
            if not isFirstFieldGoal and 'MAKE' in event['shotType']:
                break
    return summaryDict

# Additional variables'
# Top that are def worht
'''
1. Individual player scoring percent on first shot
2. player score percent overall
3. Team score precent first shot
4. Team score percent overall
5. The above but for defense (opponents)
6. Percentage of first shots taken by particular player
8. Above extended up until first basket made/for first X shots
9. Above for opponents
10. Team FT rate, two point vs. 3 point etc.
11. Number of shots until first made
12. First tip performance
13. Non standard tip
14. Low appearance tip
'''




# -	Ref (this would be complicated, but it's actually highly likely that certain refs will throw the ball in a way that benefits one other another)
# -	Is starter out
# -	Home/away - Data fetched
# -	Who they tip it to - possesion gaining player (fetched)
# -	Matchup
# -	Height - Being Fetched
# -	Offensive effectiveness
# -	Back-to-back games/overtime etc.
# -	Age decline - Being Fetched
# -	Recent history weighting

### POTENTIAL ADDITIONAL VARIABLES FOR ODDS MODEL
# Offensive Efficiency
# Defensive Efficiency
# new center record (for low Data on tipper)

# Recency bias in ranking (ARIMA model or similar)
# Season leaders
# Likely first shooter percentages
# Likely other shooter percentages
# combine vertical
# Injury
# Back to back/overtime
# Return from long absence/injury