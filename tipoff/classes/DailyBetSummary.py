class DailyBetSummary:
    def __init__(self, homeTeamOdds=None, awayTeamOdds=None, homePlayerOddsList=None, awayPlayerOddsList=None,
                 homeId=None, awayId=None, datetime=None, gameCode=None, exchange=None, url=None):
        self.homeId = homeId
        self.homeTeamOdds = homeTeamOdds
        self.awayTeamOdds = awayTeamOdds
        self.homePlayerOddsList = homePlayerOddsList
        self.awayPlayerOddsList = awayPlayerOddsList
        self.awayId = awayId
        self.datetime = datetime
        self.gameCode = gameCode
        self.exchange = exchange
        self.url = url
