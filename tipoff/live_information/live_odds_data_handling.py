# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}
from tipoff.functions.utils import sleepChecker
from tipoff.live_information.live_odds_retrieval import getStarters


def makeTeamPlayerLinePairs(playerLines, teamLines):
  pass

def createSingleOddsDict(allPlayerLines, allTeamLines):
  oddsDict = createEmptyOddsDict()
  oddsDict['home'] = None
  oddsDict['away'] = None
  oddsDict['exchange'] = None
  oddsDict['marketUrl'] = None
  pass

def createAllOddsDict(playerLines, teamLines):
    teamPlayerPairs = makeTeamPlayerLinePairs(playerLines, teamLines)
    for pair in teamPlayerPairs:
      createSingleOddsDict(pair['teamLines'], pair['playerLines'])

    pass

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
    sleepCounter = 0
    startersList = list()
    tipperList = list()
    fullJson = {}

    for teamLine in teamList:
        startersList.append({"starters": getStarters(teamLine), "team": teamLine})
        sleepCounter = sleepChecker(sleepCounter, printStop=False)

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
