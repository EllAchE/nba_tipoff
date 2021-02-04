import ENVIRONMENT
from Functions.Odds_Calculator import positiveEvThresholdFromAmerican, returnGreaterOdds, \
    convertPlayerLinesToSingleLine, getScoreProb, kellyBetFromAOddsAndScoreProb, getEvMultiplier


class GameOdds:
    def __init__(self, gameDict):
        self.homeId = gameDict['home']
        self.awayId = gameDict['away']
        self.datetime = gameDict['gameDatetime']
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
        self.homeScoreProb = getScoreProb() # todo populate these with center fetch
        self.awayScoreProb = getScoreProb()
        self.betOnHome = (self.homeScoreProb > self.minHomeWinPercentage)
        self.betOnAway = (self.awayScoreProb > self.minAwayWinPercentage)

        self.homeKellyBet = kellyBetFromAOddsAndScoreProb(self.homeScoreProb, self.homeTeamOdds)
        self.awayKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.awayTeamOdds)

        if self.homeKellyBet is not None:
            self.kellyBet = self.homeKellyBet
        else:
            self.kellyBet = self.awayKellyBet # todo assumes no same-market arbitrage ( could be possible with player/team lines varying0
        self.expectedValueMulitplierHome = getEvMultiplier(self.bestHomeOdds, self.minHomeWinPercentage)
        self.expectedValueMulitplierAway = getEvMultiplier(self.bestAwayOdds, self.minAwayWinPercentage)


