from src.classes.GameOdds import GameOdds

class FanduelGameOdds(GameOdds):
    def __init__(self, gameDict, teamOnly=False, playersOnly=False):
        super().__init__(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.homeTeamSecondQuarterOdds = gameDict['teamOdds']['homeTeamSecondQuarterOdds']
        self.awayTeamSecondQuarterOdds = gameDict['teamOdds']['awayTeamSecondQuarterOdds']
        self.homeTeamThirdQuarterOdds = gameDict['teamOdds']['homeTeamThirdQuarterOdds']
        self.awayTeamThirdQuarterOdds = gameDict['teamOdds']['awayTeamThirdQuarterOdds']
        self.homeTeamFourthQuarterOdds = gameDict['teamOdds']['homeTeamFourthQuarterOdds']
        self.awayTeamFourthQuarterOdds = gameDict['teamOdds']['awayTeamFourthQuarterOdds']

    def getBetSideOdds(self):
        if self.betOnHome:
            return self.awayTeamSecondQuarterOdds, self.awayTeamThirdQuarterOdds, self.homeTeamFourthQuarterOdds
        elif self.betOnAway:
            return self.homeTeamSecondQuarterOdds, self.homeTeamThirdQuarterOdds, self.awayTeamFourthQuarterOdds
        else:
            return None, None, None
