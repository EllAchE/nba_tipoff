from typing import Any

from src.classes.GameOdds import GameOdds
from src.live_data.live_odds_data_handling import createAllOddsDict


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

def getAllOddsAndDisplayByEv(includeDk=False, includeMgm=False, includeBovada=False):
    allOddsDictList = createAllOddsDict(includeDk=False, includeMgm=False, includeBovada=False)
    displayAllBetsByEV(allOddsDictList)

def printOddsObjDetails(oddsList: Any, showAll: bool = False):
    i = 1
    
    for g in oddsList:
        if not showAll and not g.betEither():
            continue
        betOn = g.betOn()
        floatHomeScoreProb = round(float(g.homeScoreProb), 3)
        floatMinBetOdds = round(float(g.minHomeWinPercentage), 3) if g.betOnHome else round(float(g.minAwayWinPercentage), 3)
        betOnVia = g.bestBetIsTeamOrPlayers()
        playerSpread = g.bestPlayerSpread()
        i += 1

        print(str(i) + '.', g.gameCode, "|| Bet On:", betOn, "|| Via:", betOnVia, "|| Kelly Bet:",
              g.kellyBet, "|| EV Factor:", g.bestEVFactor, "|| Tipoff:", g.gameDatetime) # ". Home/Away:", g.home, g.away,
        print("   || Tippers-H/A", g.expectedHomeTipper + '/' + g.expectedAwayTipper, "|| Odds Home Wins", floatHomeScoreProb,
              "|| Min Odds (HoDef):", floatMinBetOdds, "|| Home Line:", g.bestHomeOdds, "|| Away Line:", g.bestAwayOdds)
        print('   Exchange:', g.exchange, '|| Market URL:', g.marketUrl, '|| Odds as of:', g.fetchedDatetime, '\n')
        if betOnVia == "PLAYERS":
            print("    Player Spread:")
            for player in playerSpread:
                print('   ', player)
            print()

# Format is https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Home team 3 letter symbol is used after a 0, i.e. YYYYMMDD0###.html
#
# URL for game https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Where YYYYMMDD0### (# = home team code)
#
# game schedule in order for seasons https://www.basketball-reference.com/leagues/NBA_2019_games.html
# Games played https://www.basketball-reference.com/leagues/NBA_2019_games-october.html
# Year is ending year (i.e. 2018-2019 is 2019)
# All relevant are October-June except 2019-2020 and 2020-21 (first bc covid, second is in progress)
