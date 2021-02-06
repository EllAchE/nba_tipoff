import json

from Classes.GameOdds import GameOdds


def displayUniqueBetsByEV(betDict):
    pass


def displayUniqueBetsByEV(betDict):
    pass


def displayAllBetsByEV(betDict, showAll=True):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor)
    printOddsObjDetails(oddsList, showAll)


def displayAllBetsByDatetime(betDict, showAll=True):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor)
    oddsList.sort(key=lambda x: x.gameDatetime)
    printOddsObjDetails(oddsList, showAll)


def displayAllBetsByExchange(betDict, showAll=True):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor)
    oddsList.sort(key=lambda x: x.gameDatetime)
    oddsList.sort(key=lambda x: x.exchange)
    printOddsObjDetails(oddsList, showAll)


def convertDictToGameOddsObjList(betDict):
    gameOddsObjList = list()
    for game in betDict['games']:
        oddsObj = GameOdds(game)
        gameOddsObjList.append(oddsObj)
    return gameOddsObjList


def printOddsObjDetails(oddsList, showAll=False):
    i = 1
    for g in oddsList:
        if not showAll and not g.betEither():
            continue
        betOn = g.betOn()
        floatHomeScoreProb = round(float(g.homeScoreProb), 2)
        floatMinBetOdds = round(float(g.minHomeWinPercentage), 2) if g.betOnHome else round(float(g.minAwayWinPercentage), 2)
        betOnVia = g.bestBetIsTeamOrPlayers()
        playerSpread = g.bestPlayerSpread()

        print(str(i) + '.', g.gameCode, "|| Bet On:", betOn, "|| Via:", betOnVia, "|| Kelly Bet:", g.kellyBet, "|| EV Factor:", g.bestEVFactor, "|| Tipoff:", g.gameDatetime) # ". Home/Away:", g.home, g.away,
        print("   || Tippers-H/A", g.expectedHomeTipper + '/' + g.expectedAwayTipper,
              "|| Odds Home Wins", floatHomeScoreProb, "|| Min Odds (HoDef):", floatMinBetOdds, "|| Home Line:", g.bestHomeOdds, "|| Away Line:", g.bestAwayOdds)
        print('   Exchange:', g.exchange, '|| Market URL:', g.marketUrl, '|| Odds as of:', g.fetchedDatetime)
        print()
        if betOnVia == "PLAYERS":
            print("Player Spread:")
            for player in playerSpread:
                print(player)
            print()

        i += 1


def convertDictToGameOddsObjList(betDict):
    gameOddsObjList = list()
    for game in betDict['games']:
        oddsObj = GameOdds(game)
        gameOddsObjList.append(oddsObj)
    return gameOddsObjList


with open("Data/JSON/sample_odds_dict.json") as j:
    dict = json.load(j)
    displayAllBetsByExchange(dict)

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
