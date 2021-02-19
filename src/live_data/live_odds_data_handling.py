# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}
import json
from datetime import datetime

from src.classes.GameOdds import GameOdds
from src.functions.database_proxy import getCurrentPlayerTeam
from src.functions.utils import sleepChecker, sleepChecker
from src.live_data.live_odds_retrieval import getStarters, draftKingsOdds, mgmOdds, bovadaOdds


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
      oddsDict = addTeamOnlyToOddsDict(oddsDict)
  if playerOdds:
      oddsDict = addPlayerOnlyOddsDict(oddsDict)

  for field in kwargs: # these can be marketUrl, gameDatetime, more may come
    oddsDict[field] = rawOddsDict[field]
  return oddsDict

def createAllOddsDictForExchange(teamLines, exchange): # playerLines, exchange):
    allOddsDicts = list()
    # teamPlayerPairs = makeTeamPlayerLinePairs(teamLines) #, playerLines)
    # for pair in teamPlayerPairs:
    #   createSingleOddsDict(pair['teamLines'], pair['playerLines'])
    for gameLine in teamLines:
        allOddsDicts.append(createSingleOddsDict(gameLine, exchange))
    return allOddsDicts

def createAllOddsDict():
    dkOddsDicts = createAllOddsDictForExchange(draftKingsOdds(), 'draftkings')
    # mgmOddsDicts = createAllOddsDictForExchange(mgmOdds(), 'mgm')
    # bovadaLines = bovadaOdds()
    allOddsDictsList = list()

    for rawOddsDict in dkOddsDicts:
        allOddsDictsList.append(rawOddsDict)

    # for oddsDict in mgmOddsDicts:
    #     allOddsDictsList.append(oddsDict)

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
      "odds": {
        "homeScoreFirstOdds": None,
        "awayScoreFirstOdds": None,
        "homePlayerOdds": [
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          }
        ],
        "awayPlayerOdds": [
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          },
          {
            "player": None,
            "odds": None
          }
        ]
      }
    }


def createTeamTipperDict():
    teamList = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX',
                'BOS', 'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']
    teamList.sort()
    startersList = list()
    tipperList = list()
    fullJson = {}

    for teamLine in teamList:
        startersList.append({"starters": getStarters(teamLine), "team": teamLine})
        sleepChecker(printStop=False)

    for teamLine in startersList:
        player = teamLine["starters"][0]
        nameList = player[0].split(' ')
        lcode = ''
        i = 0
        while i < 5:
            try:
                lcode += nameList[1][i]
                i += 1
            except:
                break
        code = lcode + nameList[0][:2] + '01.html'
        code = code.lower()

        tipperList.append({"playerCode":code, "team": teamLine["team"]})
    fullJson["pairs"] = tipperList

    with open ('Data/JSON/team_tipper_pairs.json', 'w') as file:
        json.dump(fullJson, file)

def formatUnknownTeamPlayerLines(rawPlayerLines, homeShortCode=None, awayShortCode=None):
    if len(rawPlayerLines) != 10:
        raise ValueError("Must have exactly ten players right now")

    home = []
    away = []
    for player in rawPlayerLines:
        teamShortCode = getCurrentPlayerTeam(player['name'])
        if teamShortCode == homeShortCode:
            home.append({"name": player['name'], "odds": player["odds"], "team": homeShortCode})
        elif teamShortCode == awayShortCode:
            away.append({"name": player['name'], "odds": player["odds"], "team": homeShortCode})
        else:
            raise ValueError("No match for either team", homeShortCode, awayShortCode, "for player", player)

    return home, away

