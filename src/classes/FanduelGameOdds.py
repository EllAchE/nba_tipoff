from src.classes.GameOdds import GameOdds

class FanduelGameOdds(GameOdds):
    def __init__(self, gameDict, teamOnly=False, playersOnly=False):
        super().__init__(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.homeTeamSecondQuarterOddsList = gameDict['playerOdds']['awayTeamSecondQuarterOdds']
        self.awayTeamSecondQuarterOddsList = gameDict['playerOdds']['awayTeamSecondQuarterOdds']
        self.homeTeamThirdQuarterOddsList = gameDict['playerOdds']['awayTeamThirdQuarterOdds']
        self.awayTeamThirdQuarterOddsList = gameDict['playerOdds']['awayTeamThirdQuarterOdds']
        self.homeTeamFourthQuarterOddsList = gameDict['playerOdds']['awayTeamFourthQuarterOdds']
        self.awayTeamFourthQuarterOddsList = gameDict['playerOdds']['awayTeamFourthQuarterOdds']