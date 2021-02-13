from tipoff.functions.odds_calculator import convertPlayerLinesToSingleLine, returnGreaterOdds, \
    positiveEvThresholdFromAmerican, getScoreProb, kellyBetFromAOddsAndScoreProb, getEvMultiplier, getPlayerSpread
from tipoff.live_information.live_odds_retrieval import getExpectedTipper


class GameOdds:
    def __init__(self, gameDict):
        self.home = gameDict['home']
        self.away = gameDict['away']
        self.oddsDatetime = gameDict['fetchedDatetime']
        self.gameDatetime = gameDict['gameDatetime']
        self.homeTeamOdds = gameDict['odds']['homeTeamScoreFirstOdds']
        self.awayTeamOdds = gameDict['odds']['awayTeamScoreFirstOdds']
        self.homePlayerOddsList = gameDict['odds']['homePlayerOdds']
        self.awayPlayerOddsList = gameDict['odds']['awayPlayerOdds']
        self.gameCode = gameDict['gameCode']
        self.exchange = gameDict['exchange']
        self.marketUrl = gameDict['marketUrl']
        self.fetchedDatetime = gameDict['fetchedDatetime']

        self.homePlayerFloorOdds = convertPlayerLinesToSingleLine(self.homePlayerOddsList)
        self.awayPlayerFloorOdds = convertPlayerLinesToSingleLine(self.awayPlayerOddsList)
        self.bestHomeOdds = returnGreaterOdds(self.homeTeamOdds, self.homePlayerFloorOdds)
        self.bestAwayOdds = returnGreaterOdds(self.awayTeamOdds, self.awayPlayerFloorOdds)
        self.minHomeWinPercentage = positiveEvThresholdFromAmerican(self.bestHomeOdds)
        self.minAwayWinPercentage = positiveEvThresholdFromAmerican(self.bestAwayOdds)

        self.expectedHomeTipper = getExpectedTipper(self.home)
        self.expectedAwayTipper = getExpectedTipper(self.away)
        self.homeScoreProb = getScoreProb(self.expectedHomeTipper, self.expectedAwayTipper)
        self.awayScoreProb = getScoreProb(self.expectedAwayTipper, self.expectedHomeTipper)

        self.homeKellyBet = kellyBetFromAOddsAndScoreProb(self.homeScoreProb, self.homeTeamOdds)
        self.awayKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.awayTeamOdds)
        self.betOnHome = (self.homeScoreProb > self.minHomeWinPercentage)
        self.betOnAway = (self.awayScoreProb > self.minAwayWinPercentage)
        self.kellyBet = None

        if self.homeKellyBet > 0:
            self.kellyBet = {"bet": self.homeKellyBet, "team": self.home}
        elif self.awayKellyBet > 0:
            self.kellyBet = {"bet": self.awayKellyBet, "team": self.away}

        self.homeEVFactor = getEvMultiplier(self.homeScoreProb, self.minHomeWinPercentage)
        self.awayEVFactor = getEvMultiplier(self.awayScoreProb, self.minAwayWinPercentage)
        if self.awayEVFactor < self.homeEVFactor:
            self.bestEVFactor = self.homeEVFactor
        else:
            self.bestEVFactor = self.awayEVFactor

    def homeLineIsTeam(self):
        if self.bestHomeOdds == self.homeTeamOdds:
            return "TEAM"
        return "PLAYERS"

    def awayLineIsTeam(self):
        if self.bestAwayOdds == self.awayTeamOdds:
            return "TEAM"
        return "PLAYERS"

    def bestOddsFor(self):
        if self.bestEVFactor == self.homeEVFactor:
            return "HOME"
        return "AWAY"

    def betOn(self):
        if not self.betEither():
            return "NEITHER"
        elif self.betOnHome is not None:
            return "HOME"
        else:
            return "AWAY"

    def bestBetIsTeamOrPlayers(self):
        betOn = self.betOn()
        if betOn == "NEITHER":
            return "NA"
        elif betOn == "HOME":
            return self.homeLineIsTeam()
        else:
            return self.awayLineIsTeam()

    def betEither(self):
        return self.betOnHome or self.betOnAway

    def bestPlayerSpread(self):
        spread = "NA"
        if self.bestBetIsTeamOrPlayers() == "PLAYERS":
            if self.betOnHome is not None:
                spread = getPlayerSpread(self.homePlayerOddsList, self.homeScoreProb, self.homePlayerFloorOdds)
            elif self.betOnAway is not None:
                spread = getPlayerSpread(self.awayPlayerOddsList, self.awayScoreProb, self.awayPlayerFloorOdds)
        return spread

