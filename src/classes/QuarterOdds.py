from src.live_data.live_odds_retrieval import getExpectedTipper
from src.odds.odds_calculator import getEvMultiplier, getPlayerSpread, convertPlayerLinesToSingleLine, \
    positiveEvThresholdFromAmerican, returnGreaterOdds, scoreFirstProb, kellyBetFromAOddsAndScoreProb


class QuarterOdds:
    def __init__(self, gameDict, teamOnly=False, playersOnly=False, quarter="QUARTER_1"):
        self.awayPlayerFloorOdds = self.homePlayerFloorOdds = self.awayPlayerFloorOdds = self.homePlayerFloorOdds = self.awayPlayerFloorOdds = self.kellyBet = self.homeTeamFirstQuarterOdds = self.awayTeamFirstQuarterOdds = None
        self.home = gameDict['home']
        self.away = gameDict['away']
        self.fetchedDatetime = gameDict['fetchedDatetime']
        self.gameDatetime = gameDict['gameDatetime']
        self.exchange = gameDict['exchange']
        self.marketUrl = gameDict['marketUrl']
        self.isTeamOnly = teamOnly
        self.isPlayersOnly = playersOnly
        gameStart = self.fetchedDatetime[:10] if self.gameDatetime is None else self.gameDatetime
        self.gameCode = self.home + " @ " + self.away + " " + gameStart
        self.quarter = quarter
        self.isFullGame = False

        if not playersOnly:
            self.homeTeamFirstQuarterOdds = str(gameDict['teamOdds']['homeTeamFirstQuarterOdds']) if gameDict['teamOdds']['homeTeamFirstQuarterOdds'] is not None else None
            self.awayTeamFirstQuarterOdds = str(gameDict['teamOdds']['awayTeamFirstQuarterOdds']) if gameDict['teamOdds']['awayTeamFirstQuarterOdds'] is not None else None
        if not teamOnly:
            self.homePlayerOddsList = gameDict['playerOdds']['homePlayerFirstQuarterOdds']
            self.awayPlayerOddsList = gameDict['playerOdds']['awayPlayerFirstQuarterOdds']
            self.isFirstFieldGoal = gameDict['playerOdds']['isFirstFieldGoal']
        if teamOnly and playersOnly:
            raise ValueError("need at least team or player")

        if not teamOnly:
            if(len(self.homePlayerOddsList) < 5 or len(self.homePlayerOddsList) > 6):
                print("fewer than five home players for game", self.gameCode, 'odds will be None')
            elif(len(self.awayPlayerOddsList) < 5 or len(self.awayPlayerOddsList) > 6):
                print("fewer than five home players for game", self.gameCode, 'odds will be None')
            else:
                try:
                    self.homePlayerFloorOdds = convertPlayerLinesToSingleLine(self.homePlayerOddsList)
                    self.awayPlayerFloorOdds = convertPlayerLinesToSingleLine(self.awayPlayerOddsList)
                except:
                    print("player odds failed, odds will stay as None")

        if teamOnly:
            self.bestHomeOdds = self.homeTeamFirstQuarterOdds
            self.bestAwayOdds = self.awayTeamFirstQuarterOdds
        elif playersOnly:
            self.bestHomeOdds = self.homePlayerFloorOdds
            self.bestAwayOdds = self.awayPlayerFloorOdds
        elif self.homeTeamFirstQuarterOdds is None:
            self.bestHomeOdds = self.homePlayerFloorOdds
            self.bestAwayOdds = self.awayPlayerFloorOdds
        elif self.awayPlayerFloorOdds is None:
            self.bestHomeOdds = self.homeTeamFirstQuarterOdds
            self.bestAwayOdds = self.awayTeamFirstQuarterOdds
        else:
            self.bestHomeOdds = returnGreaterOdds(self.homeTeamFirstQuarterOdds, self.homePlayerFloorOdds)
            self.bestAwayOdds = returnGreaterOdds(self.awayTeamFirstQuarterOdds, self.awayPlayerFloorOdds)
        self.minHomeWinPercentage = positiveEvThresholdFromAmerican(self.bestHomeOdds)
        self.minAwayWinPercentage = positiveEvThresholdFromAmerican(self.bestAwayOdds)

        self.expectedHomeTipper = getExpectedTipper(self.home)
        self.expectedAwayTipper = getExpectedTipper(self.away)
        self.homeScoreProb = scoreFirstProb(self.expectedHomeTipper, self.expectedAwayTipper, self.quarter)
        self.awayScoreProb = scoreFirstProb(self.expectedAwayTipper, self.expectedHomeTipper, self.quarter)

        self.homeBestKellyBet = kellyBetFromAOddsAndScoreProb(self.homeScoreProb, self.bestHomeOdds)
        self.awayBestKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.bestAwayOdds)
        self.betOnHome = (self.homeScoreProb > self.minHomeWinPercentage)
        self.betOnAway = (self.awayScoreProb > self.minAwayWinPercentage)

        # if not playersOnly and self.homeTeamFirstQuarterOdds is not None:
        #     self.homeTeamKellyBet = kellyBetFromAOddsAndScoreProb(self.homeScoreProb, self.homeTeamFirstQuarterOdds)
        #     self.awayTeamKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.awayTeamFirstQuarterOdds)
        # if not teamOnly: # and self.homePlayerFloorOdds != '-200':
        #     self.homePlayersKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.homePlayerFloorOdds)
        #     self.awayPlayersKellyBet = kellyBetFromAOddsAndScoreProb(self.awayScoreProb, self.awayPlayerFloorOdds)

        if self.homeBestKellyBet > 0:
            self.kellyBet = {"bet": self.homeBestKellyBet, "team": self.home}
        elif self.awayBestKellyBet > 0:
            self.kellyBet = {"bet": self.awayBestKellyBet, "team": self.away}

        self.homeEVFactor = getEvMultiplier(self.homeScoreProb, self.minHomeWinPercentage)
        self.awayEVFactor = getEvMultiplier(self.awayScoreProb, self.minAwayWinPercentage)
        if self.awayEVFactor < self.homeEVFactor:
            self.bestEVFactor = self.homeEVFactor
            if self.homeTeamFirstQuarterOdds is None:
                self.betOnVia = "PLAYERS"
            elif self.homePlayerFloorOdds is None:
                self.betOnVia = "TEAM"
            elif self.bestHomeOdds == self.homeTeamFirstQuarterOdds:
                self.betOnVia = "TEAM"
            elif self.bestHomeOdds == self.homePlayerFloorOdds:
                self.betOnVia = "PLAYERS"
        else:
            self.bestEVFactor = self.awayEVFactor
            if self.awayTeamFirstQuarterOdds is None:
                self.betOnVia = "PLAYERS"
            elif self.awayPlayerFloorOdds is None:
                self.betOnVia = "TEAM"
            elif self.bestAwayOdds == self.awayTeamFirstQuarterOdds:
                self.betOnVia = "TEAM"
            elif self.bestAwayOdds == self.awayPlayerFloorOdds:
                self.betOnVia = "PLAYERS"

    def homeLineIsTeam(self):
        if self.bestHomeOdds == self.homeTeamFirstQuarterOdds:
            return "TEAM"
        return "PLAYERS"

    def awayLineIsTeam(self):
        if self.bestAwayOdds == self.awayTeamFirstQuarterOdds:
            return "TEAM"
        return "PLAYERS"

    def bestOddsFor(self):
        if self.bestEVFactor == self.homeEVFactor:
            return "HOME"
        return "AWAY"

    def betOn(self):
        if not self.betEither():
            return "NEITHER"
        elif self.betOnHome:
            return self.home + " (HOME)"
        else:
            return self.away + " (AWAY)"

    def bestBetIsTeamOrPlayers(self):
        betOn = self.betOn()
        if betOn == "NEITHER":
            return "NA"
        else:
            return self.betOnVia

    def betEither(self):
        return self.betOnHome or self.betOnAway

    def bestPlayerSpread(self):
        spread = "NA"
        if self.bestBetIsTeamOrPlayers() == "PLAYERS":
            if self.betOnHome:
                spread = getPlayerSpread(self.homePlayerOddsList, self.homeScoreProb, self.homePlayerFloorOdds)
            elif self.betOnAway:
                spread = getPlayerSpread(self.awayPlayerOddsList, self.awayScoreProb, self.awayPlayerFloorOdds)
        return spread

    # def betTeamOrPlayers(self):
    #     lst = list()
    #     lst.append([costFor100(self.homeTeamOdds), "TEAM"])
    #     lst.append([costFor100(self.awayTeamOdds), "TEAM"])
    #     lst.append([costFor100(self.homePlayerFloorOdds), "PLAYERS"])
    #     lst.append([costFor100(self.awayPlayerFloorOdds), "PLAYERS"])
    #
    #     def sortFn(x):
    #         return x[0]
    #
    #     lst.sort(key=sortFn)
    #     return lst[0][1]

