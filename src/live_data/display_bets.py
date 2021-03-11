from typing import Any
from datetime import datetime
import jsonpickle

from src.classes.GameOdds import GameOdds
from src.live_data.live_odds_data_handling import createAllOddsDict
# backlogtodo update player spread calculation to round


def displayUniqueBetsByEV(betDict: Any, showAll: bool = True):
    oddsList = convertDictToGameOddsObjList(betDict)
    filteredOddsList = filterBestByGameCode(oddsList)
    filteredOddsList.sort(key=lambda x: x.bestEVFactor)
    printOddsObjDetails(filteredOddsList, showAll)

def displayUniqueBetsByDatetime(betDict: Any, showAll: bool = True):
    oddsList = convertDictToGameOddsObjList(betDict)
    filteredOddsList = filterBestByGameCode(oddsList)
    filteredOddsList.sort(key=lambda x: x.bestEVFactor)
    filteredOddsList.sort(key=lambda x: x.gameDatetime)
    printOddsObjDetails(filteredOddsList, showAll)

def displayAllBetsByEV(oddsList: Any, showAll: bool = True): # backlogtodo fix typing errors with betDict to support dict[str, Any]
    oddsList.sort(key=lambda x: x.bestEVFactor, reverse=True)
    printOddsObjDetails(oddsList, showAll)

def displayAllBetsByDatetime(betDict: Any, showAll: bool = True):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor, reverse=True)
    oddsList.sort(key=lambda x: x.gameDatetime)
    printOddsObjDetails(oddsList, showAll)

def displayAllBetsByExchange(betDict: Any, showAll: bool = True):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor, reverse=True)
    oddsList.sort(key=lambda x: x.gameDatetime)
    oddsList.sort(key=lambda x: x.exchange)
    printOddsObjDetails(oddsList, showAll)

def filterBestByGameCode(oddsObjList: Any) -> Any:
    bestPerGameOnly = Any()
    gameCodes = set()

    for gameOdds in oddsObjList:
        gameCodes.add(gameOdds.gameCode)

    for gameCode in gameCodes:
        singleGameList = list(filter(lambda x: x.gameCode == gameCode, oddsObjList))
        bestPerGameOnly.append(max([x.bestEVFactor for x in singleGameList]))

    return bestPerGameOnly

def convertDictToGameOddsObjList(betDict: Any) -> Any:
    gameOddsObjList = list()

    for game in betDict['games']:
        oddsObj = GameOdds(game)
        gameOddsObjList.append(oddsObj)

    return gameOddsObjList

def saveOddsToFile(path, odds):
    with open(path, 'w') as f:
        f.write(jsonpickle.encode(odds))
        f.close()

def getAllOddsAndDisplayByEv(getDk=False, getMgm=False, getBovada=False, getPointsBet=False, getUnibet=False, getBarstool=False, getFanduel=False):
    allGameOddsObjList = createAllOddsDict(getDk=getDk, getMgm=getMgm, getBovada=getBovada, getPointsBet=getPointsBet, getUnibet=getUnibet, getBarstool=getBarstool, getFanduel=getFanduel)
    d = datetime.now().strftime("%Y-%m-%d_%H-%M-%S%p")
    saveOddsToFile(f"Data/JSON/historical_odds/{d}.json", allGameOddsObjList)
    displayAllBetsByEV(allGameOddsObjList)

def printOddsObjDetails(oddsList: Any, showAll: bool = False, showTeamAndPlayers: bool = False):
    i = 0

    for g in oddsList:
        if not showAll and not g.betEither():
            continue
        betOn = g.betOn()
        floatHomeScoreProb = round(float(g.homeScoreProb), 3)
        if betOn == "NEITHER":
            floatMinBetOdds = round(float(g.minHomeWinPercentage), 3)
        else:
            floatMinBetOdds = round(float(g.minHomeWinPercentage), 3) if g.betOnHome else round(float(g.minAwayWinPercentage), 3)
        betOnVia = g.bestBetIsTeamOrPlayers()
        playerSpread = g.bestPlayerSpread()

        print(str(i) + '.', g.gameCode, "|| Bet On:", betOn, "|| Via:", betOnVia, "|| Kelly Bet:",
              g.kellyBet, "|| EV Factor:", g.bestEVFactor)#, "|| Tipoff:", g.gameDatetime)
        print('   Exchange:', g.exchange, '|| Odds as of:', g.fetchedDatetime)  # '|| Market URL:', g.marketUrl,
        print("   || Tippers-H/A", g.expectedHomeTipper + '/' + g.expectedAwayTipper, "|| Odds Home Wins", floatHomeScoreProb,
              "|| Min Odds:", floatMinBetOdds, "|| Home Line:", g.bestHomeOdds, "|| Away Line:", g.bestAwayOdds, '\n')

        if showTeamAndPlayers: # Assumes this is only set this way if both exist
            print("kelly bet home team odds", g.homeTeamKellyBet)
            print("kelly bet away team odds", g.awayTeamKellyBet)
            print("kelly bet home player odds", g.homePlayersKellyBet)
            print("kelly bet away player odds", g.awayPlayersKellyBet)

        if betOnVia == "PLAYERS":
            print("    Player Spread:")
            playerTotalCost = 0
            for player in playerSpread:
                print('   ', player)
                playerTotalCost += player['bet']
            print("     Total Bet Amount:", playerTotalCost)
            if g.exchange == "bovada":
                print("THIS IS BOVADA. All odds calculations are run twice as odds cannot be matched to team.")
                print("Odds on site may not reflect prints here")

            if g.isFirstFieldGoal:
                print("    * This is for first field goal only")
            print()


        i += 1
