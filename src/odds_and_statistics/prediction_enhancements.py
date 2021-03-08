# backlogtodo offensive rebounding/defensive rebounding influence
# backlogtodo add other stats and run ludwig/ai checker
import json
from collections import OrderedDict
import requests
import ENVIRONMENT
from src.utils import lowercaseNoSpace

# backlogtodo include nonshooting possessions
# todo these should be done:
#    Offensive efficiency, Def E, Percentage of FT & 2s vs. 3s (effective score percentage), usage rate for players

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

def getFirstShotStats(season):
    stub = ENVIRONMENT.SINGLE_SEASON_SHOTS_BEFORE_FIRST_FG_PATH
    with open(stub.format(season)) as data:
        firstShotsDict = json.load(data)

    summaryDict = {}
    makesOverall = 0

    summaryDict = _initializePlayerDict(summaryDict, firstShotsDict)
    summaryDict = _initializeTeamDict(summaryDict, firstShotsDict)

    for game in firstShotsDict:
        summaryDict, makesOverall = _playerFirstShotStats(game, summaryDict, makesOverall)
        summaryDict = _teamFirstShotStats(game, summaryDict)

    summaryDict = _summaryStats(summaryDict)

    summaryDict = OrderedDict(sorted(summaryDict.items(), key=lambda item: list(item)[1]['quarter1']['totalMakes'], reverse=True))
    savePath = ENVIRONMENT.FIRST_SHOT_SUMMARY_UNFORMATTED_PATH.format(str(season))
    with open(savePath, 'w') as writeFile:
        json.dump(summaryDict, writeFile, indent=4)
    print('first shot statistics compiled. Total makes was counted as', makesOverall)

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
            summaryDict[player][quarter] = {'shots': 0, '2PT MAKE': 0, '3PT MAKE': 0, 'FREE THROW MAKE': 0, 'FG ATTEMPTS': 0,
                               '2PT MISS': 0, '3PT MISS': 0, 'FREE THROW MISS': 0, 'FREE THROW ATTEMPTS': 0,
                               'firstShotIndex': 0, 'firstShots': 0, 'averageShotIndex': 0, 'gamesStarted': None,
                               'totalMakes': 0, 'teams': [], 'favorableTipResults': 0}  # backlogtodo get games started as a separate stat
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
            summaryDict[team][quarter] = {'favorableTipResults': 0, 'shots': 0, '2PT MAKE': 0, '3PT MAKE': 0, 'FREE THROW MAKE': 0,
                                          'FG ATTEMPTS': 0, 'shootingStarters': [], '2PT MISS': 0, '3PT MISS': 0, 'FREE THROW MISS': 0,
                                          'FREE THROW ATTEMPTS': 0, 'firstShotIndex': 0, 'firstShots': 0, 'totalMakes': 0,
                                          'opponentFgAttempts': 0, 'opponentFtAttempts': 0, 'opponent2ptmake': 0, 'opponent2ptmiss': 0,
                                          'opponent3ptmake': 0, 'opponent3ptmiss': 0, 'opponentfreethrowmake': 0, 'opponentfreethrowmiss': 0,
                                          'opponentShots': 0, 'opponentTotalMakes': 0}
    return summaryDict

def _teamFirstShotStats(game, summaryDict):
    # todo add in tip result to quarter data
    # todo group quarters 1 and 4 as 'tip wins', 2 & 3 as 'tip losses'
    quarters = ['quarter1', 'quarter2', 'quarter3', 'quarter4']
    for quarter in quarters:
        for event in game[quarter]:
            team = event['team']
            opponent = event['opponentTeam']
            summaryDict[team][quarter]['shots'] += 1
            summaryDict[opponent][quarter]['opponentShots'] += 1
            summaryDict[team][quarter][event['shotType']] += 1
            summaryDict[opponent][quarter][lowercaseNoSpace('opponent' + event['shotType'])] += 1

            if '2PT' in event['shotType'] or '3PT' in event['shotType']:
                summaryDict[team][quarter]['FG ATTEMPTS'] += 1
                summaryDict[opponent][quarter]['opponentFgAttempts'] += 1
            else:
                summaryDict[team][quarter]['FREE THROW ATTEMPTS'] += 1
                summaryDict[opponent][quarter]['opponentFtAttempts'] += 1
            if 'MAKE' in event['shotType']:
                summaryDict[team][quarter]['totalMakes'] += 1
                summaryDict[opponent][quarter]['opponentTotalMakes'] += 1

    return summaryDict

def _summaryStats(summaryDict):
    for playerOrTeam in summaryDict:
        try:
            summaryDict[playerOrTeam]['shootingPercentage'] = (summaryDict[playerOrTeam]['2PT MAKE'] + summaryDict[playerOrTeam]['3PT MAKE'])\
                                                        / summaryDict[playerOrTeam]['FG ATTEMPTS']
        except:
            summaryDict[playerOrTeam]['shootingPercentage'] = None
        try:
            summaryDict[playerOrTeam]['freeThrowPercentage'] = (summaryDict[playerOrTeam]['FREE THROW MAKE']) / summaryDict[playerOrTeam]['FREE THROW ATTEMPTS']
        except:
            summaryDict[playerOrTeam]['freeThrowPercentage'] = None

    return summaryDict

def _playerFirstShotStats(game, summaryDict, makesOverall):
    playerHasShotInGame = set()
    quarters = ['quarter1']#, 'quarter2', 'quarter3', 'quarter4']
    # only consider first quarter shots for individual players currently
    # todo normalize for games started, compare to known player usage rate for a given season
    # todo add in tip result to quarter data

    for quarter in quarters:
        for event in game[quarter]:
            player = event['player']
            playerTeam = event['team']
            if playerTeam not in summaryDict[player][quarter]['teams']:
                summaryDict[player][quarter]['teams'].append(playerTeam)
            summaryDict[player][quarter]['averageShotIndex'] = (summaryDict[player][quarter]['shots'] * summaryDict[player][quarter][
                'averageShotIndex'] + event['shotIndex']) / (summaryDict[player][quarter]['shots'] + 1)

            if player not in playerHasShotInGame:
                summaryDict[player][quarter]['firstShotIndex'] = (summaryDict[player][quarter]['shots'] * summaryDict[player][quarter][
                    'firstShotIndex'] + event['shotIndex']) / (summaryDict[player][quarter]['shots'] + 1)
            playerHasShotInGame.add(player)
            summaryDict[player][quarter]['shots'] += 1
            summaryDict[player][quarter][event['shotType']] += 1
            if event['shotIndex'] == 1:
                summaryDict[player][quarter]['firstShots'] += 1
            if '2PT' in event['shotType'] or '3PT' in event['shotType']:
                summaryDict[player][quarter]['FG ATTEMPTS'] += 1
            else:
                summaryDict[player][quarter]['FREE THROW ATTEMPTS'] += 1
            if 'MAKE' in event['shotType']:
                summaryDict[player][quarter]['totalMakes'] += 1
                makesOverall += 1
    return summaryDict, makesOverall

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