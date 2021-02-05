class AnalyzedGameOdds:
    def __init__(self, rawGameOdds, bankroll):
        self.homeId = rawGameOdds.home
        self.awayId = rawGameOdds.away
        self.datetime = rawGameOdds.gameDatetime
        self.homeTeamOdds = rawGameOdds.homeTeamOdds
        self.awayTeamOdds = rawGameOdds.awayTeamOdds
        self.homePlayerOddsList = rawGameOdds.homePlayerOddsList
        self.awayPlayerOddsList = rawGameOdds.awayPlayerOddsList
        self.gameCode = rawGameOdds.gameCode
        self.exchange = rawGameOdds.exchange
        self.url = rawGameOdds.url
        self.homeKellyBet
        self.awayKellyBet
        self.expectedValueMultiplier
        self.requiredWinPercentage
        self.expectedWinPercentage
        self.bankroll = bankroll

