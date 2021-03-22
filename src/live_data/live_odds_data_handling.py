# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}
from datetime import datetime

from src.classes.FullGameOdds import FullGameOdds
from src.classes.QuarterOdds import QuarterOdds
from src.database.database_access import getUniversalPlayerName
from src.live_data.live_odds_retrieval import draftKingsOdds, mgmOdds, bovadaOdds, pointsBetOdds, unibetOdds, \
    barstoolOdds, fanduelOddsToday, fanduelOddsTomorrow, betfairOdds
from src.odds_and_statistics.odds_calculator import americanToDecimal
import logging


def addTeamOnlyToOddsDict(oddsDict, rawOddsDict):
    oddsDict['teamOdds']['homeTeamFirstQuarterOdds'] = rawOddsDict['homeTeamFirstQuarterOdds']
    oddsDict['teamOdds']['awayTeamFirstQuarterOdds'] = rawOddsDict['awayTeamFirstQuarterOdds']
    try:
        oddsDict['teamOdds']["homeTeamSecondQuarterOdds"] = rawOddsDict["homeTeamSecondQuarterOdds"]
        oddsDict['teamOdds']["awayTeamSecondQuarterOdds"] = rawOddsDict["awayTeamSecondQuarterOdds"]
        oddsDict['teamOdds']["homeTeamThirdQuarterOdds"] = rawOddsDict["homeTeamThirdQuarterOdds"]
        oddsDict['teamOdds']["awayTeamThirdQuarterOdds"] = rawOddsDict["awayTeamThirdQuarterOdds"]
        oddsDict['teamOdds']["homeTeamFourthQuarterOdds"] = rawOddsDict["homeTeamFourthQuarterOdds"]
        oddsDict['teamOdds']["awayTeamFourthQuarterOdds"] = rawOddsDict["awayTeamFourthQuarterOdds"]
    except:
        pass
    return oddsDict

def addPlayerOnlyOddsDict(oddsDict, rawOddsDict):
    oddsDict['playerOdds']['homePlayerFirstQuarterOdds'] = rawOddsDict['homePlayerFirstQuarterOdds']
    oddsDict['playerOdds']['awayPlayerFirstQuarterOdds'] = rawOddsDict['awayPlayerFirstQuarterOdds']
    if 'isFirstFieldGoal' in rawOddsDict.keys():
        oddsDict['playerOdds']['isFirstFieldGoal'] = rawOddsDict['isFirstFieldGoal']
    return oddsDict


def createSingleOddsDict(rawOddsDict, playerOdds=True, teamOdds=True, *kwargs):#, allPlayerLines,):
  oddsDict = createEmptyOddsDict()
  oddsDict['fetchedDatetime'] = str(datetime.now())
  oddsDict['home'] = rawOddsDict['home']
  oddsDict['away'] = rawOddsDict['away']
  oddsDict['exchange'] = rawOddsDict['exchange']
  oddsDict['gameCode'] = rawOddsDict['home'] + " @ " + rawOddsDict['away'] + " " + oddsDict['fetchedDatetime'][:10]

  if teamOdds:
      oddsDict = addTeamOnlyToOddsDict(oddsDict, rawOddsDict)
  if playerOdds:
      oddsDict = addPlayerOnlyOddsDict(oddsDict, rawOddsDict)

  for field in kwargs: # these can be marketUrl, gameDatetime, more may come
    oddsDict[field] = rawOddsDict[field]
  return oddsDict

def createAllOddsDictForExchange(allGameDictsFromExchange, playerOdds=True, teamOdds=True): # playerLines, exchange):
    allOddsDicts = list()
    for rawGameDict in allGameDictsFromExchange:
        allOddsDicts.append(createSingleOddsDict(rawGameDict, playerOdds=playerOdds, teamOdds=teamOdds))
    return allOddsDicts

def createOptimalPlayerSpreadObject(gameOddsObjList):
    optimalSpreadsList = list()
    emptyOddsDict = createEmptyOddsDict()
    gameCodeDict = {}

    bestPlayerOddsDict = {}
    for game in gameOddsObjList:
        if game.isTeamOnly:
            continue
        gameCodeDict[game.gameCode] = {"home": game.home, "away": game.away}

    for game in gameOddsObjList:
        try:
            for line in (game.homePlayerOddsList + game.awayPlayerOddsList):
                universalName = getUniversalPlayerName(line['player'])
                try:
                    if americanToDecimal(bestPlayerOddsDict[universalName]['odds']) < americanToDecimal(line['odds']):
                        bestPlayerOddsDict[universalName]['odds'] = line['odds']
                        bestPlayerOddsDict[universalName]['exchange'] = game.exchange
                except: # backlogtodo shouldn;t use except to see if key is populated
                    bestPlayerOddsDict[universalName] = line
                    bestPlayerOddsDict[universalName]['exchange'] = game.exchange
        except:
            print(game.gameCode, 'from exchange', game.exchange, 'Not used in optimized player spread. It was misformatted/may have lacked odds.')

    for gameCodeKey in gameCodeDict:
        tempOddsDict = emptyOddsDict
        tempOddsDict['gameCode'] = gameCodeKey
        tempOddsDict['home'] = gameCodeDict[gameCodeKey]['home']
        tempOddsDict['away'] = gameCodeDict[gameCodeKey]['away']
        tempOddsDict['exchange'] = "OPTIMAL PLAYER SPREAD"
        for key in bestPlayerOddsDict.keys():
            if bestPlayerOddsDict[key]['team'] == tempOddsDict['home']:
                tempOddsDict['playerOdds']['homePlayerFirstQuarterOdds'].append(bestPlayerOddsDict[key])
            elif bestPlayerOddsDict[key]['team'] == tempOddsDict['away']:
                tempOddsDict['playerOdds']['awayPlayerFirstQuarterOdds'].append(bestPlayerOddsDict[key])
        optimalSpreadsList.append(QuarterOdds(tempOddsDict, playersOnly=True))

    return optimalSpreadsList

def _addFullGameOddsObjsToList(allGameObjList, method, exchangeErrorText, teamOnly=True, playersOnly=False):
    try:
        oddsDicts = createAllOddsDictForExchange(method(), teamOdds=(not playersOnly), playerOdds=(not teamOnly))
        for rawOddsDict in oddsDicts:
            gameOddsObj = FullGameOdds(rawOddsDict, teamOnly=teamOnly, playersOnly=playersOnly)
            allGameObjList.append(gameOddsObj)
        print('fetched {}'.format(exchangeErrorText), '\n')
    except:
        logging.exception('breaking error in {}.'.format(exchangeErrorText))
    return allGameObjList

def _addSingleQuarterOddsObjsToList(allGameObjList, method, exchangeErrorText, teamOnly=True, playersOnly=False):
    try:
        oddsDicts = createAllOddsDictForExchange(method(), teamOdds=(not playersOnly), playerOdds=(not teamOnly))
        for rawOddsDict in oddsDicts:
            gameOddsObj = QuarterOdds(rawOddsDict, teamOnly=teamOnly, playersOnly=playersOnly)
            allGameObjList.append(gameOddsObj)
        print('fetched {}'.format(exchangeErrorText), '\n')
    except:
        logging.exception('breaking error in {}.'.format(exchangeErrorText))
    return allGameObjList

def createAllOddsDict(draftkings=False, fanduelToday=False, fanduelTomorrow=False, mgm=False, bovada=False,
                      pointsBet=False, unibet=False, barstool=False, betfair=False, includeOptimalPlayerSpread=False):
    allGameObjList = list()

    if fanduelToday:
        allGameObjList = _addFullGameOddsObjsToList(allGameObjList, fanduelOddsToday, "fanduel odds for today", teamOnly=False, playersOnly=False)
    if fanduelTomorrow:
        allGameObjList = _addFullGameOddsObjsToList(allGameObjList, fanduelOddsTomorrow, "fanduel odds for tomorrow", teamOnly=False, playersOnly=False)
    if betfair:
        allGameObjList = _addFullGameOddsObjsToList(allGameObjList, betfairOdds, "betfair odds", teamOnly=True, playersOnly=False)
    if draftkings:
        allGameObjList = _addSingleQuarterOddsObjsToList(allGameObjList, draftKingsOdds, "draftkings odds", teamOnly=False, playersOnly=False)
    if mgm:
        allGameObjList = _addSingleQuarterOddsObjsToList(allGameObjList, mgmOdds, "mgm odds", teamOnly=True, playersOnly=False)
    if bovada:
        allGameObjList = _addSingleQuarterOddsObjsToList(allGameObjList, bovadaOdds, "bovada odds", teamOnly=False, playersOnly=False)
    if pointsBet:
        allGameObjList = _addSingleQuarterOddsObjsToList(allGameObjList, pointsBetOdds, "pointsbet odds", teamOnly=False, playersOnly=True)
    if unibet:
        allGameObjList = _addSingleQuarterOddsObjsToList(allGameObjList, unibetOdds, "unibet odds", teamOnly=False, playersOnly=True)
    if barstool:
        allGameObjList = _addSingleQuarterOddsObjsToList(allGameObjList, barstoolOdds, "barstool odds", teamOnly=False, playersOnly=True)

    if includeOptimalPlayerSpread:
        try:
            optimalPlayerSpreads = createOptimalPlayerSpreadObject(allGameObjList)
            for obj in optimalPlayerSpreads:
                allGameObjList.append(obj)
            print('got optimized player spread', '\n')
        except:
            logging.exception('breaking error creating optimal player spread.')

    return allGameObjList # backlogtodo this dict can be saved for reference for backtesting

def createEmptyOddsDict():
    return {
      "gameCode": None,
      "gameDatetime": None,
      "home": None,
      "away": None,
      "exchange": None,
      "marketUrl": None,
      "fetchedDatetime": None,
      "teamOdds": {
        "homeTeamFirstQuarterOdds": None,
        "awayTeamFirstQuarterOdds": None,
        "homeTeamSecondQuarterOdds": None,
        "awayTeamSecondQuarterOdds": None,
        "homeTeamThirdQuarterOdds": None,
        "awayTeamThirdQuarterOdds": None,
        "homeTeamFourthQuarterOdds": None,
        "awayTeamFourthQuarterOdds": None,
      },
        "playerOdds": {
        "isFirstFieldGoal": False,
        "homePlayerFirstQuarterOdds": [],
        "awayPlayerFirstQuarterOdds": []
      }
    }
