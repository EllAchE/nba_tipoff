from src.classes.QuarterOdds import QuarterOdds

class FullGameOdds(QuarterOdds):
    def __init__(self, gameDict, teamOnly=False, playersOnly=False):
        super().__init__(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.isFullGame = True
        self.homeTeamSecondQuarterOdds = gameDict['teamOdds']['homeTeamSecondQuarterOdds']
        self.awayTeamSecondQuarterOdds = gameDict['teamOdds']['awayTeamSecondQuarterOdds']
        self.homeTeamThirdQuarterOdds = gameDict['teamOdds']['homeTeamThirdQuarterOdds']
        self.awayTeamThirdQuarterOdds = gameDict['teamOdds']['awayTeamThirdQuarterOdds']
        self.homeTeamFourthQuarterOdds = gameDict['teamOdds']['homeTeamFourthQuarterOdds']
        self.awayTeamFourthQuarterOdds = gameDict['teamOdds']['awayTeamFourthQuarterOdds']
        teamOnly = True

        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamSecondQuarterOdds
        gameDict['teamOdds']['awayTeamFirstQuarterOdds'] = self.awayTeamSecondQuarterOdds
        self.secondQuarterGameObj = QuarterOdds(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.secondQuarterGameObj.quarter = "QUARTER_2"
        self.secondQuarterGameObj.isFullGame = True
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamThirdQuarterOdds
        gameDict['teamOdds']['awayTeamFirstQuarterOdds'] = self.awayTeamThirdQuarterOdds
        self.thirdQuarterGameObj = QuarterOdds(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.thirdQuarterGameObj.quarter = "QUARTER_3"
        self.thirdQuarterGameObj.isFullGame = True
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamFourthQuarterOdds
        gameDict['teamOdds']['awayTeamFirstQuarterOdds'] = self.awayTeamFourthQuarterOdds
        self.fourthQuarterGameObj = QuarterOdds(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.fourthQuarterGameObj.quarter = "QUARTER_4"
        self.fourthQuarterGameObj.isFullGame = True

    def getBetSideOdds(self):
        if self.betOnHome:
            return self.awayTeamSecondQuarterOdds, self.awayTeamThirdQuarterOdds, self.homeTeamFourthQuarterOdds
        elif self.betOnAway:
            return self.homeTeamSecondQuarterOdds, self.homeTeamThirdQuarterOdds, self.awayTeamFourthQuarterOdds
        else:
            return None, None, None
