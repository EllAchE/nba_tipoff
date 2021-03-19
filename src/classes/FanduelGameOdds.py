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
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamSecondQuarterOdds
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamSecondQuarterOdds
        self.secondQuarterGameObj = GameOdds(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly, isQuarter1Or4=False)
        self.secondQuarterGameObj.quarter = "QUARTER_2"
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamThirdQuarterOdds
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamThirdQuarterOdds
        self.thirdQuarterGameObj = GameOdds(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly, isQuarter1Or4=False)
        self.secondQuarterGameObj.quarter = "QUARTER_3"
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamFourthQuarterOdds
        gameDict['teamOdds']['homeTeamFirstQuarterOdds'] = self.homeTeamFourthQuarterOdds
        self.fourthQuarterGameObj = GameOdds(gameDict=gameDict, teamOnly=teamOnly, playersOnly=playersOnly)
        self.secondQuarterGameObj.quarter = "QUARTER_4"


    def getBetSideOdds(self):
        if self.betOnHome:
            return self.awayTeamSecondQuarterOdds, self.awayTeamThirdQuarterOdds, self.homeTeamFourthQuarterOdds
        elif self.betOnAway:
            return self.homeTeamSecondQuarterOdds, self.homeTeamThirdQuarterOdds, self.awayTeamFourthQuarterOdds
        else:
            return None, None, None
