from typing import Any
from datetime import datetime
import jsonpickle

from src.classes.QuarterOdds import QuarterOdds
from src.live_data.live_odds_data_handling import createAllOddsDict
# backlogtodo update player spread calculation to round


def displayUniqueBetsByEV(oddsList, showAll: bool = True):
    filteredOddsList = filterBestByGameCode(oddsList)
    filteredOddsList.sort(key=lambda x: x.bestEVFactor)
    printOddsObjDetails(filteredOddsList, showAll)

def displayUniqueBetsByDatetime(oddsList, showAll: bool = True):
    filteredOddsList = filterBestByGameCode(oddsList)
    filteredOddsList.sort(key=lambda x: x.bestEVFactor)
    filteredOddsList.sort(key=lambda x: x.gameDatetime)
    printOddsObjDetails(filteredOddsList, showAll)

def displayAllBetsByEV(oddsList: Any, showAll: bool = True): # backlogtodo fix typing errors with betDict to support dict[str, Any]
    oddsList.sort(key=lambda x: x.bestEVFactor, reverse=True)
    printOddsObjDetails(oddsList, showAll)

def displayAllBetsByDatetime(oddsList, showAll: bool = True):
    oddsList.sort(key=lambda x: x.bestEVFactor, reverse=True)
    oddsList.sort(key=lambda x: x.gameDatetime)
    printOddsObjDetails(oddsList, showAll)

def displayAllBetsByExchange(oddsList, showAll: bool = True):
    oddsList.sort(key=lambda x: x.bestEVFactor, reverse=True)
    oddsList.sort(key=lambda x: x.gameDatetime)
    oddsList.sort(key=lambda x: x.exchange)
    printOddsObjDetails(oddsList, showAll)

def filterBestByGameCode(oddsObjList):
    bestPerGameOnly = list()
    gameCodes = set()

    for gameOdds in oddsObjList:
        gameCodes.add(gameOdds.gameCode)

    for gameCode in gameCodes:
        singleGameList = list(filter(lambda x: x.gameCode == gameCode, oddsObjList))
        bestPerGameOnly.append(max(singleGameList, key= lambda x: x.bestEVFactor))

    bestPerGameOnly.sort(key=lambda x: x.bestEVFactor)

    return bestPerGameOnly

def saveOddsToFile(path, odds):
    with open(path, 'w') as f:
        f.write(jsonpickle.encode(odds))
        f.close()

def getAllOddsAndDisplayByExchange(draftkings=False, mgm=False, bovada=False, pointsbet=False, unibet=False, barstool=False, fanduelToday=False, fanduelTomorrow=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(draftkings=draftkings, mgm=mgm, bovada=bovada, pointsBet=pointsbet, unibet=unibet, barstool=barstool, fanduelToday=fanduelToday, fanduelTomorrow=fanduelTomorrow, betfair=betfair, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    d = datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
    saveOddsToFile(f'Data/JSON/historical_odds/{d}.json', allGameOddsObjList)
    displayAllBetsByExchange(allGameOddsObjList)

def getAllOddsAndDisplayByEv(draftkings=False, mgm=False, bovada=False, pointsbet=False, unibet=False, barstool=False, fanduelToday=False, fanduelTomorrow=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(draftkings=draftkings, mgm=mgm, bovada=bovada, pointsBet=pointsbet, unibet=unibet, barstool=barstool, fanduelToday=fanduelToday, fanduelTomorrow=fanduelTomorrow, betfair=betfair, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    d = datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
    saveOddsToFile(f'Data/JSON/historical_odds/{d}.json', allGameOddsObjList)
    displayAllBetsByEV(allGameOddsObjList)

# backlogtodo bovada breaks this by having unknown teams.
def getUniqueOddsAndDisplayByEv(draftkings=False, mgm=False, bovada=False, pointsbet=False, unibet=False, barstool=False, fanduelToday=False, fanduelTomorrow=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(draftkings=draftkings, mgm=mgm, bovada=bovada, pointsBet=pointsbet, unibet=unibet, barstool=barstool, fanduelToday=fanduelToday, fanduelTomorrow=fanduelTomorrow, betfair=betfair, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    d = datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
    saveOddsToFile(f'Data/JSON/historical_odds/{d}.json', allGameOddsObjList)
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

    if not g.isFullGame:
        print(str(i) + '.', g.gameCode + ' ' + g.quarter, '|| Bet On:', betOn, '|| Via:', betOnVia, '|| Kelly Bet:',
              g.kellyBet, '|| EV Factor:', g.bestEVFactor)  # , '|| Tipoff:', g.gameDatetime)
        print('   Exchange:', g.exchange, '|| Odds as of:', g.fetchedDatetime)  # '|| Market URL:', g.marketUrl,
        print('   || Tippers-H/A', g.expectedHomeTipper + '/' + g.expectedAwayTipper, '|| Odds Home Wins',
              floatHomeScoreProb,
              '|| Min Odds:', floatMinBetOdds, '|| Home Line:', g.bestHomeOdds, '|| Away Line:', g.bestAwayOdds)
    elif g.isFullGame and g.quarter == "QUARTER_1":
        print(str(i) + '.', g.gameCode, 'Full Game Results', 'Exchange:', g.exchange, '|| Odds as of:', g.fetchedDatetime)
        print('   || Tippers-H/A', g.expectedHomeTipper + '/' + g.expectedAwayTipper, '|| Odds Home Wins',
              floatHomeScoreProb, '|| Min Odds:', floatMinBetOdds)
    else:
        print('   ', g.quarter, '|| Bet On:', betOn, '|| Via:', betOnVia, '|| Kelly Bet:', g.kellyBet, '|| EV Factor:', g.bestEVFactor, '|| Home Line:', g.bestHomeOdds, '|| Away Line:', g.bestAwayOdds)

    if showTeamAndPlayers:  # Assumes this is only set this way if both exist
        print('kelly bet home team odds', g.homeTeamKellyBet)
        print('kelly bet away team odds', g.awayTeamKellyBet)
        print('kelly bet home player odds', g.homePlayersKellyBet)
        print('kelly bet away player odds', g.awayPlayersKellyBet)

    if betOnVia == 'PLAYERS':
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
    if g.isFullGame:
        if g.quarter == "QUARTER_4":
            print()
    else:
        print()

def printFullGameDetails(g, showTeamAndPlayers, i):
    printQuarterDetails(g, showTeamAndPlayers, i)
    printQuarterDetails(g.secondQuarterGameObj, showTeamAndPlayers, i)
    printQuarterDetails(g.thirdQuarterGameObj, showTeamAndPlayers, i)
    printQuarterDetails(g.fourthQuarterGameObj, showTeamAndPlayers, i)

    # printQuarterDetails(g.thirdQuarterGameObj, showTeamAndPlayers, i)
    # printQuarterDetails(g.fourthQuarterGameObj, showTeamAndPlayers, i)

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
