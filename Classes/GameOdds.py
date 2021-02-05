from Functions.Odds_Calculator import positiveEvThresholdFromAmerican, returnGreaterOdds, \
    convertPlayerLinesToSingleLine, getScoreProb, kellyBetFromAOddsAndScoreProb, getEvMultiplier
from Live_Information.Live_Odds_Retrieval import getExpectedTipper


class GameOdds:
    def __init__(self, gameDict):
        self.home = gameDict['home']
        self.away = gameDict['away']
        self.gameDatetime = gameDict['gameDatetime']
        self.homeTeamOdds = gameDict['odds']['homeTeamScoreFirstOdds']
        self.awayTeamOdds = gameDict['odds']['awayTeamScoreFirstOdds']
        self.homePlayerOddsList = gameDict['odds']['homePlayerOdds']
        self.awayPlayerOddsList = gameDict['odds']['awayPlayerOdds']
        self.gameCode = gameDict['gameCode']
        self.exchange = gameDict['exchange']
        self.url = gameDict['url']

        self.minHomeWinPercentage = positiveEvThresholdFromAmerican(self.homeTeamOdds)
        self.minAwayWinPercentage = positiveEvThresholdFromAmerican(self.awayTeamOdds)
        self.homePlayerFloorOdds = convertPlayerLinesToSingleLine(self.homePlayerOddsList)
        self.awayPlayerFloorOdds = convertPlayerLinesToSingleLine(self.awayPlayerOddsList)
        self.bestHomeOdds = returnGreaterOdds(self.homeTeamOdds, self.homePlayerFloorOdds)
        self.bestAwayOdds = returnGreaterOdds(self.awayTeamOdds, self.awayPlayerFloorOdds)

        self.expectedHomeCenter = getExpectedTipper(self.home)
        self.expectedAwayCenter = getExpectedTipper(self.away)
        self.homeScoreProb = getScoreProb(self.expectedHomeCenter, self.expectedAwayCenter) # todo populate these with center fetch
        self.awayScoreProb = getScoreProb(self.expectedAwayCenter, self.expectedHomeCenter)

        self.betOnHome = (self.homeScoreProb > self.minHomeWinPercentage)
        self.betOnAway = (self.awayScoreProb > self.minAwayWinPercentage)
        self.homeKellyBet = kellyBetFromAOddsAndScoreProb(self.homeScoreProb, self.homeTeamOdds)
        self.awayKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.awayTeamOdds)

        if self.homeKellyBet is not None:
            self.kellyBet = {"bet": self.homeKellyBet, "team": self.home}
        else:
            self.kellyBet = {"bet": self.awayKellyBet, "team": self.away} # todo assumes no same-market arbitrage ( could be possible with player/team lines varying)

        self.evFactorHome = getEvMultiplier(self.bestHomeOdds, self.minHomeWinPercentage)
        self.evFactorAway = getEvMultiplier(self.bestAwayOdds, self.minAwayWinPercentage)
        if self.evFactorAway < self.evFactorHome:
            self.bestEVFactor = self.evFactorHome
        else:
            self.bestEVFactor = self.evFactorAway


