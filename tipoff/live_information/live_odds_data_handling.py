# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}


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
