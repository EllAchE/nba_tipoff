# assume odds look like - {team1: odds, team2: odds}, {playerName: odds}

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

def createOddsDict(playerLines, teamLines):
    oddsDict = createEmptyOddsDict()
    allTeams = set()


