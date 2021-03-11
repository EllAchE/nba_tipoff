from src.classes.GameOdds import GameOdds

class FanduelGameOdds(GameOdds):
    def __init__(self, gameDict, teamOnly=False, playersOnly=False):
        super().__init__(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.homeTeamSecondQuarterOdds = gameDict['teamOdds']['awayTeamSecondQuarterOdds']
        self.awayTeamSecondQuarterOdds = gameDict['teamOdds']['awayTeamSecondQuarterOdds']
        self.homeTeamThirdQuarterOdds = gameDict['teamOdds']['awayTeamThirdQuarterOdds']
        self.awayTeamThirdQuarterOdds = gameDict['teamOdds']['awayTeamThirdQuarterOdds']
        self.homeTeamFourthQuarterOdds = gameDict['teamOdds']['awayTeamFourthQuarterOdds']
        self.awayTeamFourthQuarterOdds = gameDict['teamOdds']['awayTeamFourthQuarterOdds']