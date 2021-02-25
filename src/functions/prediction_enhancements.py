# backlogtodo offensive rebounding/defensive rebounding influence
# backlogtodo add other stats and run ludwig/ai checker
import json
from collections import OrderedDict


# backlogtodo include nonshooting possessions
from src.functions.utils import lowercaseNoSpace

# todo these should be done:
#    Offensive efficiency, Def E, Percentage of FT & 2s vs. 3s (effective score percentage)

def getFirstShotStats(season):
    with open('../../Data/JSON/Public_NBA_API/shots_before_first_field_goal.json') as data:
        firstShotsDict = json.load(data)

    lastSeasonData = firstShotsDict[str(season)]
    summaryDict = {}
    makesOverall = 0

    summaryDict = _initializePlayerDict(summaryDict, lastSeasonData)
    summaryDict = _initializeTeamDict(summaryDict, lastSeasonData)

    for game in lastSeasonData:
        summaryDict, makesOverall = _playerFirstShotStats(game, summaryDict, makesOverall)
        summaryDict = _teamFirstShotStats(game, summaryDict)

    summaryDict = _summaryStats(summaryDict)

    summaryDict = OrderedDict(sorted(summaryDict.items(), key=lambda item: list(item)[1]['totalMakes'], reverse=True))
    with open('../../Data/JSON/Public_NBA_API/player_first_shot_summary.json', 'w') as writeFile:
        json.dump(summaryDict, writeFile)
    print('first shot statistics compiled. Total makes was counted as', makesOverall)

def _initializePlayerDict(summaryDict, lastSeasonData):
    playerSet = set()
    for game in lastSeasonData:
        for event in game['gameData']:
            playerSet.add(event['player'])

    for player in playerSet:
        summaryDict[player] = {"shots": 0, "2PT MAKE": 0, "3PT MAKE": 0, "FREE THROW MAKE": 0, "FG ATTEMPTS": 0,
                               "2PT MISS": 0, "3PT MISS": 0, "FREE THROW MISS": 0, "FREE THROW ATTEMPTS": 0,
                               'firstShotIndex': 0, "firstShots": 0, "averageShotIndex": 0, "gamesStarted": None,
                               "totalMakes": 0, "teams": []}  # backlogtodo get games started as a separate stat
    return summaryDict

def _initializeTeamDict(summaryDict, lastSeasonData):
    teamSet = set()
    for game in lastSeasonData:
        for event in game['gameData']:
            teamSet.add(event['team'])

    for team in teamSet:
        summaryDict[team] = {"shots": 0, "2PT MAKE": 0, "3PT MAKE": 0, "FREE THROW MAKE": 0, "FG ATTEMPTS": 0, "shootingStarters": [],
                             "2PT MISS": 0, "3PT MISS": 0, "FREE THROW MISS": 0, "FREE THROW ATTEMPTS": 0, 'firstShotIndex': 0,
                             "firstShots": 0, "totalMakes": 0, "opponentFgAttempts": 0, "opponentFtAttempts": 0, "opponent2ptmake": 0, "opponent2ptmiss": 0,
                             "opponent3ptmake": 0, "opponent3ptmiss": 0, "opponentfreethrowmake": 0, "opponentfreethrowmiss": 0,
                             'opponentShots': 0, 'opponentTotalMakes': 0}
    return summaryDict

def _teamFirstShotStats(game, summaryDict):
    for event in game['gameData']:
        team = event['team']
        opponent = event['opponentTeam']
        summaryDict[team]['shots'] += 1
        summaryDict[opponent]['opponentShots'] += 1
        summaryDict[team][event['shotType']] += 1
        summaryDict[opponent][lowercaseNoSpace('opponent' + event['shotType'])] += 1

        if "2PT" in event['shotType'] or "3PT" in event['shotType']:
            summaryDict[team]['FG ATTEMPTS'] += 1
            summaryDict[opponent]['opponentFgAttempts'] += 1
        else:
            summaryDict[team]['FREE THROW ATTEMPTS'] += 1
            summaryDict[opponent]['opponentFtAttempts'] += 1
        if "MAKE" in event['shotType']:
            summaryDict[team]['totalMakes'] += 1
            summaryDict[opponent]['opponentTotalMakes'] += 1

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
    for event in game['gameData']:
        player = event['player']
        playerTeam = event['team']
        if playerTeam not in summaryDict[player]['teams']:
            summaryDict[player]['teams'].append(playerTeam)
        summaryDict[player]['averageShotIndex'] = (summaryDict[player]['shots'] * summaryDict[player][
            'averageShotIndex'] + event['shotIndex']) / (summaryDict[player]['shots'] + 1)

        if player not in playerHasShotInGame:
            summaryDict[player]['firstShotIndex'] = (summaryDict[player]['shots'] * summaryDict[player][
                'firstShotIndex'] + event['shotIndex']) / (summaryDict[player]['shots'] + 1)
        playerHasShotInGame.add(player)
        summaryDict[player]['shots'] += 1
        summaryDict[player][event['shotType']] += 1
        if event['shotIndex'] == 1:
            summaryDict[player]['firstShots'] += 1
        if "2PT" in event['shotType'] or "3PT" in event['shotType']:
            summaryDict[player]['FG ATTEMPTS'] += 1
        else:
            summaryDict[player]['FREE THROW ATTEMPTS'] += 1
        if "MAKE" in event['shotType']:
            summaryDict[player]['totalMakes'] += 1
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