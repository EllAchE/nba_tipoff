# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}
import json
from datetime import datetime

from src.classes.FanduelGameOdds import FanduelGameOdds
from src.classes.GameOdds import GameOdds
from src.database.database_access import getUniversalPlayerName
from src.live_data.live_odds_retrieval import draftKingsOdds, mgmOdds, bovadaOdds, pointsBetOdds, unibetOdds, \
    barstoolOdds, fanduelOddsToday, fanduelOddsTomorrow
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
        optimalSpreadsList.append(GameOdds(tempOddsDict, playersOnly=True))

    return optimalSpreadsList


def createAllOddsDict(getDk=False, getFanduelToday=False, getFanduelTomorrow=False, getMgm=False, getBovada=False, getPointsBet=False, getUnibet=False, getBarstool=False, includeOptimalPlayerSpread=False):
    allGameObjList = list()

    if getFanduelToday:
        try:
            fanduelOddsDicts = createAllOddsDictForExchange(fanduelOddsToday())
            for rawOddsDict in fanduelOddsDicts:
                gameOddsObj = FanduelGameOdds(rawOddsDict)
                allGameObjList.append(gameOddsObj)
            print('fetched fanduel odds (For Today)', '\n')
        except:
            logging.exception('breaking error in fanduel odds for today. Debug when time permits')

    if getFanduelTomorrow:
        try:
            fanduelOddsDicts = createAllOddsDictForExchange(fanduelOddsTomorrow())
            for rawOddsDict in fanduelOddsDicts:
                gameOddsObj = FanduelGameOdds(rawOddsDict)
                allGameObjList.append(gameOddsObj)
            print('fetched fanduel odds (For Tomorrow)', '\n')
        except:
            logging.exception('breaking error in fanduel odds for tomorrow. ')

    if getDk:
        try:
            dkOddsDicts = createAllOddsDictForExchange(draftKingsOdds())
            for rawOddsDict in dkOddsDicts:
                gameOddsObj = GameOdds(rawOddsDict)
                allGameObjList.append(gameOddsObj)
            print('fetched drafkings odds', '\n')
        except:
            logging.exception('breaking error fetching draftkings odds.')

    if getMgm:
        try:
            mgmDicts = createAllOddsDictForExchange(mgmOdds(), playerOdds=False)
            for rawOddsDict in mgmDicts:
                gameOddsObj = GameOdds(rawOddsDict, teamOnly=True)
                allGameObjList.append(gameOddsObj)
            print('fetched mgm odds', '\n')
        except:
            logging.exception('breaking error fetching mgm odds.')

    if getBovada:
        try:
            bovadaDicts = createAllOddsDictForExchange(bovadaOdds(), playerOdds=False)
            for rawOddsDict in bovadaDicts:
                gameOddsObj = GameOdds(rawOddsDict, teamOnly=True)
                allGameObjList.append(gameOddsObj)
            print('fetched bovada odds', '\n')
        except:
            logging.exception('breaking error fetching bovada odds.')

    if getPointsBet:
        try:
            pointsBetDicts = createAllOddsDictForExchange(pointsBetOdds(), teamOdds=False)
            for rawOddsDict in pointsBetDicts:
                gameOddsObj = GameOdds(rawOddsDict, playersOnly=True)
                allGameObjList.append(gameOddsObj)
            print('fetched pointsbet odds', '\n')
        except:
            logging.exception('breaking error fetching pointsbet odds.')

    if getUnibet:
        try:
            unibetOddsDicts = createAllOddsDictForExchange(unibetOdds(), teamOdds=False)
            for rawOddsDict in unibetOddsDicts:
                gameOddsObj = GameOdds(rawOddsDict, playersOnly=True)
                allGameObjList.append(gameOddsObj)
            print('fetched unibet odds', '\n')
        except:
            logging.exception('breaking error fetching unibet odds.')

    if getBarstool:
        try:
            barstoolOddsDicts = createAllOddsDictForExchange(barstoolOdds(), teamOdds=False)
            for rawOddsDict in barstoolOddsDicts:
                gameOddsObj = GameOdds(rawOddsDict, playersOnly=True)
                allGameObjList.append(gameOddsObj)
            print('fetched barstool odds', '\n')
        except:
            logging.exception('breaking error fetching barstool odds.')

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


# def createOptimalPlayerSpreadObject(gameOddsObjList):
#     optimalSpreadsList = list()
#     emptyOddsDict = createEmptyOddsDict()
#     gameCodeSet = set()
#     teamBestLineDict = {}
#     for game in gameOddsObjList:
#         if game.isTeamOnly:
#             continue
#         gameCodeSet.add({"code": game.gameCode, "home": game.home, "away": game.away})
#         teamBestLineDict[game.home] = []
#         teamBestLineDict[game.away] = []
#
#     for game in gameOddsObjList:
#         homePlayerLines = game.homePlayerOddsList
#         awayPlayerLines = game.awayPlayerOddsList
#
#         for line in homePlayerLines:
#             name = getUniversalPlayerName(line['player'])
#             listLen = len(teamBestLineDict[game.home])
#             i = 0
#             while i < listLen:
#                 if name == getUniversalPlayerName(teamBestLineDict[game.home][i]) and americanToDecimal(teamBestLineDict[game.home][i]['odds']) > americanToDecimal(line['odds']):
#                     teamBestLineDict[game.home][i]['odds'] = line['odds']
#
#         for line in awayPlayerLines:
#             name = getUniversalPlayerName(line['player'])
#             listLen = len(teamBestLineDict[game.away])
#             i = 0
#             while i < listLen:
#                 if name == getUniversalPlayerName(teamBestLineDict[game.away][i]):
#                     if americanToDecimal(teamBestLineDict[game.away][i]['odds']) > americanToDecimal(line['odds']):
#                         teamBestLineDict[game.away][i]['odds'] = line['odds']
#                 else:
#                     teamBestLineDict[]
#
#     for gameCodeAndTeamNames in gameCodeSet:
#         tempOddsDict = emptyOddsDict
#         tempOddsDict['gameCode'] = gameCodeAndTeamNames['code']
#         tempOddsDict['home'] = gameCodeAndTeamNames['home']
#         tempOddsDict['away'] = gameCodeAndTeamNames['away']
#         tempOddsDict['playerOdds']['homePlayerScoreFirstOdds'] = teamBestLineDict[gameCodeSet['home']]
#         tempOddsDict['playerOdds']['awayPlayerScoreFirstOdds'] = teamBestLineDict[gameCodeSet['away']]
#         optimalSpreadsList.append(GameOdds(tempOddsDict, playersOnly=True))
