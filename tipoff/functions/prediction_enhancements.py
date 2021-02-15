# todo offensive rebounding/defensive rebounding influence
# todo add other stats and run ludwig/ai checker
import json
from collections import OrderedDict


# todo extend this beyond first make to just look at early shooting percentage
# todo add summary stats to compare first things being ft vs. fg
# todo add team splits
# todo add tip win conditionals to this
# todo include nonshooting possessions to help with the above
def getPlayerFirstShotStats(season):
    with open('../../Data/JSON/Public_NBA_API/shots_before_first_score.json') as data:
        firstShotsDict = json.load(data)

    lastSeasonData = firstShotsDict[str(season)]
    summaryDict = {}
    makesOverall = 0

    summaryDict = _initializePlayerDict(summaryDict, lastSeasonData)
    summaryDict = _initializeTeamDict(summaryDict, lastSeasonData)

    for game in lastSeasonData:
        summaryDict, makesOverall = _playerFirstShotStats(game, summaryDict, makesOverall)

    for player in summaryDict:
        try:
            summaryDict[player]['shootingPercentage'] = (summaryDict[player]['2PT MAKE'] + summaryDict[player][
                '3PT MAKE']) / summaryDict[player]['FG ATTEMPTS']
        except:
            summaryDict[player]['shootingPercentage'] = None
        try:
            summaryDict[player]['freeThrowPercentage'] = (summaryDict[player]['FREE THROW MAKE']) / \
                                                         summaryDict[player][
                                                             'FREE THROW ATTEMPTS']
        except:
            summaryDict[player]['freeThrowPercentage'] = None

    summaryDict = OrderedDict(sorted(summaryDict.items(), key=lambda item: list(item)[1]['totalMakes'], reverse=True))
    with open('../../Data/JSON/Public_NBA_API/player_first_shot_summary.json', 'w') as writeFile:
        json.dump(summaryDict, writeFile)
    print('first shot statistics compiled. Total makes was counted as', makesOverall)

def _initializeTeamDict(summaryDict, lastSeasonData):
    teamSet = set()
    for game in lastSeasonData:
        for event in game['gameData']:
            teamSet.add(event['team'])

    for team in teamSet:
        summaryDict[team] = {"shots": 0, "2PT MAKE": 0, "3PT MAKE": 0, "FREE THROW MAKE": 0, "FG ATTEMPTS": 0, "shootingStarters": [],
                             "2PT MISS": 0, "3PT MISS": 0, "FREE THROW MISS": 0, "FREE THROW ATTEMPTS": 0, 'firstShotIndex': 0,
                             "firstShots": 0, "totalMakes": 0, "opponentShots": 0, "opponent2ptMakes": 0, "opponent2ptMisses": 0,
                             "opponent3ptMakes": 0, "opponent3ptMisses": 0, "opponentFreeThrowMakes": 0}
    return summaryDict

def _initializePlayerDict(summaryDict, lastSeasonData):
    playerSet = set()
    for game in lastSeasonData:
        for event in game['gameData']:
            playerSet.add(event['player'])

    for player in playerSet:
        summaryDict[player] = {"shots": 0, "2PT MAKE": 0, "3PT MAKE": 0, "FREE THROW MAKE": 0, "FG ATTEMPTS": 0,
                               "2PT MISS": 0, "3PT MISS": 0, "FREE THROW MISS": 0, "FREE THROW ATTEMPTS": 0,
                               'firstShotIndex': 0, "firstShots": 0, "averageShotIndex": 0, "gamesStarted": None,
                               "totalMakes": 0, "teams": []}  # todo get games started as a separate stat
    return summaryDict


def _teamFirstShotStats(game, summaryDict):
    pass

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


# getPlayerFirstShotStats(2021)



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