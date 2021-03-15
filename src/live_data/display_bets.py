from typing import Any
from datetime import datetime
import jsonpickle

from src.classes.GameOdds import GameOdds
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

    bestPerGameOnly.sort(key=lambda x: x.bestEVFactor, reverse=True)

    return bestPerGameOnly

def saveOddsToFile(path, odds):
    with open(path, 'w') as f:
        f.write(jsonpickle.encode(odds))
        f.close()

def getAllOddsAndDisplayByEv(getDk=False, getMgm=False, getBovada=False, getPointsBet=False, getUnibet=False, getBarstool=False, getFanduelToday=False, getFanduelTomorrow=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(getDk=getDk, getMgm=getMgm, getBovada=getBovada, getPointsBet=getPointsBet, getUnibet=getUnibet, getBarstool=getBarstool, getFanduelToday=getFanduelToday, getFanduelTomorrow=getFanduelTomorrow, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    d = datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
    saveOddsToFile(f'Data/JSON/historical_odds/{d}.json', allGameOddsObjList)
    displayAllBetsByEV(allGameOddsObjList)

# todo bovada breaks this by having unknown ev items
def getUniqueOddsAndDisplayByEv(getDk=False, getMgm=False, getBovada=False, getPointsBet=False, getUnibet=False, getBarstool=False, getFanduelToday=False, getFanduelTomorrow=False, includeOptimalPlayerSpread=False):
    allGameOddsObjList = createAllOddsDict(getDk=getDk, getMgm=getMgm, getBovada=getBovada, getPointsBet=getPointsBet, getUnibet=getUnibet, getBarstool=getBarstool, getFanduelToday=getFanduelToday, getFanduelTomorrow=getFanduelTomorrow, includeOptimalPlayerSpread=includeOptimalPlayerSpread)
    d = datetime.now().strftime('%Y-%m-%d_%H-%M-%S%p')
    saveOddsToFile(f'Data/JSON/historical_odds/{d}.json', allGameOddsObjList)
    displayUniqueBetsByEV(allGameOddsObjList)

def printOddsObjDetails(oddsList: Any, showAll: bool = False, showTeamAndPlayers: bool = False):
    i = 0

    for g in oddsList:
        if not showAll and not g.betEither():
            continue
        betOn = g.betOn()
        floatHomeScoreProb = round(float(g.homeScoreProb), 3)
        if betOn == 'NEITHER':
            floatMinBetOdds = round(float(g.minHomeWinPercentage), 3)
        else:
            floatMinBetOdds = round(float(g.minHomeWinPercentage), 3) if g.betOnHome else round(float(g.minAwayWinPercentage), 3)
        betOnVia = g.bestBetIsTeamOrPlayers()
        playerSpread = g.bestPlayerSpread()

        print(str(i) + '.', g.gameCode, '|| Bet On:', betOn, '|| Via:', betOnVia, '|| Kelly Bet:',
              g.kellyBet, '|| EV Factor:', g.bestEVFactor)#, '|| Tipoff:', g.gameDatetime)
        print('   Exchange:', g.exchange, '|| Odds as of:', g.fetchedDatetime)  # '|| Market URL:', g.marketUrl,
        print('   || Tippers-H/A', g.expectedHomeTipper + '/' + g.expectedAwayTipper, '|| Odds Home Wins', floatHomeScoreProb,
              '|| Min Odds:', floatMinBetOdds, '|| Home Line:', g.bestHomeOdds, '|| Away Line:', g.bestAwayOdds)
        if g.exchange == 'fanduel':
            q2, q3, q4 = g.getBetSideOdds()
            if q2 is not None:
                print('Fanduel additional odds after - Q2: {} Q3: {} Q4: {}'.format(q2, q3, q4))
        print()

        if showTeamAndPlayers: # Assumes this is only set this way if both exist
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
            print()

        i += 1
