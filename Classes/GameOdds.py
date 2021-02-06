from Functions.Odds_Calculator import positiveEvThresholdFromAmerican, returnGreaterOdds, \
    convertPlayerLinesToSingleLine, getScoreProb, kellyBetFromAOddsAndScoreProb, getEvMultiplier, getPlayerSpread


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
        self.gameCode = gameDict['gameCode'] #todo need this to be consistent across exchanges. Can be a teamname/code
        self.exchange = gameDict['exchange']
        self.url = gameDict['marketUrl']

        self.minHomeWinPercentage = positiveEvThresholdFromAmerican(self.homeTeamOdds)
        self.minAwayWinPercentage = positiveEvThresholdFromAmerican(self.awayTeamOdds)
        self.homePlayerFloorOdds = convertPlayerLinesToSingleLine(self.homePlayerOddsList)
        self.awayPlayerFloorOdds = convertPlayerLinesToSingleLine(self.awayPlayerOddsList)
        self.bestHomeOdds = returnGreaterOdds(self.homeTeamOdds, self.homePlayerFloorOdds)
        self.bestAwayOdds = returnGreaterOdds(self.awayTeamOdds, self.awayPlayerFloorOdds)
        self.playerSpread = getPlayerSpread(self.homePlayerOddsList, self.homeScoreProb, )


        self.expectedHomeTipper = 'onealsh01.html' # lo.getExpectedTipper(self.home)
        self.expectedAwayTipper = 'turnemy01.html'  # lo.getExpectedTipper(self.away) # todo populate these with center fetch
        self.homeScoreProb = getScoreProb(self.expectedHomeTipper, self.expectedAwayTipper)
        self.awayScoreProb = getScoreProb(self.expectedAwayTipper, self.expectedHomeTipper)

        self.betOnHome = (self.homeScoreProb > self.minHomeWinPercentage)
        self.betOnAway = (self.awayScoreProb > self.minAwayWinPercentage)
        self.homeKellyBet = kellyBetFromAOddsAndScoreProb(self.homeScoreProb, self.homeTeamOdds)
        self.awayKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.awayTeamOdds)

        if self.homeKellyBet is not None:
            self.kellyBet = {"bet": self.homeKellyBet, "team": self.home}
        else:
            self.kellyBet = {"bet": self.awayKellyBet, "team": self.away} # todo assumes no same-market arbitrage (possible with player/team lines varying)

        self.homeEVFactor = getEvMultiplier(self.homeScoreProb, self.minHomeWinPercentage)
        self.awayEVFactor = getEvMultiplier(self.awayScoreProb, self.minAwayWinPercentage)
        if self.awayEVFactor < self.homeEVFactor:
            self.bestEVFactor = self.homeEVFactor

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
        return not (self.betOnHome is None and self.betOnAway is None)

    def bestPlayerSpread(self, winAmt=None, riskAmt= None):
        spread = "NA"
        if self.betOnHome is not None:
            spread = getPlayerSpread(self.homePlayerOddsList, self.homeScoreProb, self.homePlayerFloorOdds)
        elif self.betOnAway is not None:
            spread = getPlayerSpread(self.awayPlayerOddsList, self.awayScoreProb, self.awayPlayerFloorOdds)
        return spread

