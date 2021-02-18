# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}
import json

from tipoff.classes.GameOdds import GameOdds
from tipoff.functions.utils import sleepChecker, sleepChecker
from tipoff.live_information.live_odds_retrieval import getStarters, draftKingsOdds, mgmOdds, bovadaOdds


def makeTeamPlayerLinePairs(playerLines, teamLines):
  pass

def createSingleOddsDict(singleTeamLine, exchange):#, allPlayerLines,):
  oddsDict = createEmptyOddsDict()
  oddsDict['home'] = list(singleTeamLine.keys())[0] #todo this is a hack bc we don;'t care who is home vs. away
  oddsDict['away'] = list(singleTeamLine.keys())[1]
  oddsDict['exchange'] = exchange
  oddsDict['homeScoreFirstOdds'] = singleTeamLine[oddsDict['home']]
  oddsDict['awayScoreFirstOdds'] = singleTeamLine[oddsDict['away']]
  return oddsDict # todo this is bare bones for team

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

    for oddsDict in dkOddsDicts:
        print(oddsDict, 'dk')
        allOddsDictsList.append(oddsDict)

    # for oddsDict in mgmOddsDicts:
    #     print(oddsDict, 'mgm')
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
