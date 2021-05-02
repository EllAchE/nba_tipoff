import json
from typing import Any
from datetime import datetime
import jsonpickle

from src.classes.QuarterOdds import QuarterOdds
from src.live_data.live_odds_data_handling import createAllOddsDict
# backlogtodo update player spread calculation to round

def sortHelper(list, sortCategoryList): # pass arguments in the order they should be sorted in
    for sortCat in sortCategoryList:
        if sortCat == 'bestEVFactor':
            list.sort(key=lambda x: x.bestEVFactor, reverse=True)
        elif sortCat == 'gameDatetime':
            list.sort(key=lambda x: x.gameDatetime)
        elif sortCat == 'exchange':
            list.sort(key=lambda x: x.exchange)
        elif sortCat == 'gameCode':
            list.sort(key=lambda x: x.gameCode)
    return list

def displayUniqueBetsByEV(oddsList, showAll= True):
    filteredOddsList = filterBestByGameCode(oddsList)
    filteredOddsList = sortHelper(filteredOddsList, ['bestEVFactor'])
    printOddsObjDetails(filteredOddsList, showAll)

def displayUniqueBetsByDatetime(oddsList, showAll= True):
    filteredOddsList = filterBestByGameCode(oddsList)
    filteredOddsList = sortHelper(filteredOddsList, ['bestEVFactor', 'gameDatetime'])
    printOddsObjDetails(filteredOddsList, showAll)

def displayAllBetsByEV(oddsList: Any, showAll= True): # backlogtodo fix typing errors with betDict to support dict[str, Any]
    oddsList = sortHelper(oddsList, ['bestEVFactor'])
    printOddsObjDetails(oddsList, showAll)

def displayAllBetsByDatetime(oddsList, showAll= True):
    oddsList = sortHelper(oddsList, ['bestEVFactor', 'gameDatetime'])
    printOddsObjDetails(oddsList, showAll)

def displayAllBetsByExchange(oddsList, showAll= True):
    oddsList = sortHelper(oddsList, ['bestEVFactor', 'gameCode', 'exchange'])
    printOddsObjDetails(oddsList, showAll)

def filterBestByGameCode(oddsObjList):
    bestPerGameOnly = list()
    gameCodeSet = {gameOdds.gameCode for gameOdds in oddsObjList}

    for gameCode in gameCodeSet:
        singleGameList = list(filter(lambda x: x.gameCode == gameCode, oddsObjList))
        bestPerGameOnly.append(max(singleGameList, key= lambda x: x.bestEVFactor))

    bestPerGameOnly.sort(key=lambda x: x.bestEVFactor)

    return bestPerGameOnly

def saveOddsToFile(path, allGameOddsObjList, includeGameSummaryJson=True):
    with open(path, 'w') as f:
        f.write(jsonpickle.encode(allGameOddsObjList))
        f.close()

    if includeGameSummaryJson:
        oddsDict = {}
        oddsDict['games'] = []
        teamSet = set()
        for game in allGameOddsObjList:
            if game.home not in teamSet:
                teamSet.add(game.home)
                oddsDict[game.home] = {}
            if game.away not in teamSet:
                teamSet.add(game.away)
                oddsDict[game.away] = {}
            oddsDict[game.home][game.exchange] = game.bestHomeOdds
            oddsDict[game.away][game.exchange] = game.bestAwayOdds
            sortGameCode = [game.home, game.away]
            sortGameCode.sort()
            if sortGameCode[0] + " " + sortGameCode[1] not in oddsDict['games']:
                oddsDict['games'] += [sortGameCode[0] + " " + sortGameCode[1]]
        with open('tempGameOdds.json', 'w') as tempF:
            json.dump(oddsDict, tempF, indent=4) # todo test the game summary

def savePickledOddsObjs(allGameOddsObjList):
    d = datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
    saveOddsToFile(f'Data/JSON/historical_odds/{d}.json', allGameOddsObjList)

def getAllOddsAndDisplayByExchange(draftkings=False, mgm=False, bovada=False, pointsbet=False, unibet=False, barstool=False, fanduelToday=False, fanduelTomorrow=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(draftkings=draftkings, mgm=mgm, bovada=bovada, pointsBet=pointsbet, unibet=unibet, barstool=barstool, fanduelToday=fanduelToday, fanduelTomorrow=fanduelTomorrow, betfair=betfair, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    savePickledOddsObjs(allGameOddsObjList)
    displayAllBetsByExchange(allGameOddsObjList)

def getAllOddsAndDisplayByEv(draftkings=False, mgm=False, bovada=False, pointsbet=False, unibet=False, barstool=False, fanduelToday=False, fanduelTomorrow=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(draftkings=draftkings, mgm=mgm, bovada=bovada, pointsBet=pointsbet, unibet=unibet, barstool=barstool, fanduelToday=fanduelToday, fanduelTomorrow=fanduelTomorrow, betfair=betfair, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    savePickledOddsObjs(allGameOddsObjList)
    displayAllBetsByEV(allGameOddsObjList)

# backlogtodo bovada breaks this by having unknown teams.
def getUniqueOddsAndDisplayByEv(draftkings=False, mgm=False, bovada=False, pointsbet=False, unibet=False, barstool=False, fanduelToday=False, fanduelTomorrow=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(draftkings=draftkings, mgm=mgm, bovada=bovada, pointsBet=pointsbet, unibet=unibet, barstool=barstool, fanduelToday=fanduelToday, fanduelTomorrow=fanduelTomorrow, betfair=betfair, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    savePickledOddsObjs(allGameOddsObjList)
    displayUniqueBetsByEV(allGameOddsObjList)

def printQuarterDetails(g, showTeamAndPlayers, i):
    betOn = g.betOn()
    floatHomeScoreProb = round(float(g.homeScoreProb), 3)
    if betOn == 'NEITHER':
        floatMinBetOdds = round(float(g.minHomeWinPercentage), 3)
    else:
        floatMinBetOdds = round(float(g.minHomeWinPercentage), 3) if g.betOnHome else round(
            float(g.minAwayWinPercentage), 3)
    betOnVia = g.bestBetIsTeamOrPlayers()
    playerSpread = g.bestPlayerSpread()

    if g.kellyBet is not None:
        pKellyBet = "{:.3f}".format(float(g.kellyBet['bet']), 'on', g.kellyBet['team']) # todo fix this formatting
    else:
        pKellyBet = "NA"
    pEVFactor = "{:.3f}".format(float(g.bestEVFactor))

    if not g.isFullGame:
        printSingleQuarterOddsDetails(betOn, betOnVia, floatHomeScoreProb, floatMinBetOdds, g, i, pEVFactor, pKellyBet)
    elif g.isFullGame and g.quarter == "QUARTER_1":
        printFirstQuarterOfFullGameObj(floatHomeScoreProb, floatMinBetOdds, g, i)

    if g.isFullGame:
        printNonFirstQuarterForFullGameObj(betOn, betOnVia, g, pEVFactor, pKellyBet)

    if showTeamAndPlayers:  # Assumes this is only set this way if both exist
        printTeamAndPlayerKellyBets(g)

    if betOnVia == 'PLAYERS':
        printPlayerSpread(g, playerSpread)

    if g.isFullGame:
        if g.quarter == "QUARTER_4":
            print()
    else:
        print()

def printPlayerSpread(g, playerSpread):
    print('    Player Spread:')
    playerTotalCost = 0
    for player in playerSpread:
        print('   ', player)
        playerTotalCost += player['bet']
    print('     Total Bet Amount:', playerTotalCost)
    if g.exchange == 'bovada':
        print('THIS IS BOVADA. All odds calculations are run twice as odds cannot be matched to team.')
        print('Odds on site may not reflect prints here')
    if g.isFirstFieldGoal:
        print('    * This is for first field goal only')

def printNonFirstQuarterForFullGameObj(betOn, betOnVia, g, pEVFactor, pKellyBet):
    print('   ', g.quarter, '|| Bet On:', betOn, '|| Via:', betOnVia, '|| Kelly Bet:', pKellyBet, '|| EV Factor:',
          pEVFactor, '|| Home Line:', "{:.1f}".format(float(g.bestHomeOdds)), '|| Away Line:',
          "{:.1f}".format(float(g.bestAwayOdds)))

def printFirstQuarterOfFullGameObj(floatHomeScoreProb, floatMinBetOdds, g, i):
    print(str(i) + '.', g.gameCode, 'Full Game Results', 'Exchange:', g.exchange, '|| Odds as of:', g.fetchedDatetime)
    print('   || Tippers-H/A', g.expectedHomeTipper + '/' + g.expectedAwayTipper, '|| Odds Home Wins',
          floatHomeScoreProb, '|| Min Odds:', floatMinBetOdds)

def printSingleQuarterOddsDetails(betOn, betOnVia, floatHomeScoreProb, floatMinBetOdds, g, i, pEVFactor, pKellyBet):
    print(str(i) + '.', g.gameCode + ' ' + g.quarter, '|| Bet On:', betOn, '|| Via:', betOnVia, '|| Kelly Bet:',
          pKellyBet, '|| EV Factor:', pEVFactor)  # , '|| Tipoff:', g.gameDatetime)
    print('   Exchange:', g.exchange, '|| Odds as of:', g.fetchedDatetime)  # '|| Market URL:', g.marketUrl,
    print('   || Tippers-H/A', g.expectedHomeTipper + '/' + g.expectedAwayTipper, '|| Odds Home Wins',
          floatHomeScoreProb,
          '|| Min Odds:', floatMinBetOdds, '|| Home Line:', g.bestHomeOdds, '|| Away Line:', g.bestAwayOdds)

def printTeamAndPlayerKellyBets(g):
    print('kelly bet home team odds', g.homeTeamKellyBet)
    print('kelly bet away team odds', g.awayTeamKellyBet)
    print('kelly bet home player odds', g.homePlayersKellyBet)
    print('kelly bet away player odds', g.awayPlayersKellyBet)

def printFullGameDetails(g, showTeamAndPlayers, i):
    printQuarterDetails(g, showTeamAndPlayers, i)
    printQuarterDetails(g.secondQuarterGameObj, showTeamAndPlayers, i)
    printQuarterDetails(g.thirdQuarterGameObj, showTeamAndPlayers, i)
    printQuarterDetails(g.fourthQuarterGameObj, showTeamAndPlayers, i)

def printOddsObjDetails(oddsList: Any, showAll: bool = False, showTeamAndPlayers: bool = False):
    i = 0
    for g in oddsList:
        if not showAll and not g.betEither():
            continue
        if g.isFullGame:
            printFullGameDetails(g, showTeamAndPlayers, i)
        else:
            printQuarterDetails(g, showTeamAndPlayers, i)
        i += 1
