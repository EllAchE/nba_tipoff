# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}
import json
from datetime import datetime

from src.live_data.live_odds_retrieval import draftKingsOdds, mgmOdds, bovadaOdds


def makeTeamPlayerLinePairs(playerLines, teamLines):
  pass

def addTeamOnlyToOddsDict(oddsDict, rawOddsDict):
    oddsDict['teamOdds']['homeTeamFirstQuarterOdds'] = rawOddsDict['homeTeamFirstQuarterOdds']
    oddsDict['teamOdds']['awayTeamFirstQuarterOdds'] = rawOddsDict['awayTeamFirstQuarterOdds']
    return oddsDict

def addPlayerOnlyOddsDict(oddsDict, rawOddsDict):
    oddsDict['playerOdds']['homePlayerFirstQuarterOdds'] = rawOddsDict['homePlayerFirstQuarterOdds']
    oddsDict['playerOdds']['awayPlayerFirstQuarterOdds'] = rawOddsDict['awayPlayerFirstQuarterOdds']
    return oddsDict


def createSingleOddsDict(rawOddsDict, playerOdds=True, teamOdds=True, *kwargs):#, allPlayerLines,):
  oddsDict = createEmptyOddsDict()
  oddsDict['fetchedDatetime'] = str(datetime.now)
  oddsDict['home'] = rawOddsDict['home']
  oddsDict['away'] = rawOddsDict['away']
  oddsDict['exchange'] = rawOddsDict['exchange']

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

def createAllOddsDict():
    # dkOddsDicts = createAllOddsDictForExchange(draftKingsOdds(), 'draftkings')
    mgmOddsDicts = createAllOddsDictForExchange(mgmOdds(), playerOdds=False)
    bovadaLines = createAllOddsDictForExchange(bovadaOdds(), playerOdds=False)
    allOddsDictsList = list()

    # for rawOddsDict in dkOddsDicts:
    #     allOddsDictsList.append(rawOddsDict)

    for oddsDict in mgmOddsDicts:
        allOddsDictsList.append(oddsDict)

    for oddsDict in bovadaLines:
        allOddsDictsList.append(oddsDict)

    return {"games": allOddsDictsList} # backlogtodo this dict can be saved for reference for backtesting

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
      },
        "playerOdds": {
        "homePlayerFirstQuarterOdds": [],
        "awayPlayerFirstQuarterOdds": []
      }
    }
