class Player:
    def __init__(self, playerCode=None):
        self.playerCode = playerCode
        self.mu = None
        self.sigma = None
        self.firstScores = None
        self.firstShots = None
        self.currentTeam = None
        self.isTipperForTeam = None
        self.tipAppearances = None
        self.tipWins = None
        self.tipLosses = None
        self.oddsToTakeFirstShot = None
        self.shootingPercentageOnFirstShot = None
        self.oddsToMakeFirstShot = None
        self.additionalInfoDict = {}

    def setPlayerCode(self, playerCode):
        self.playerCode = playerCode

    def setMu(self, mu):
        self.mu = mu

    def setSigma(self, sigma):
        self.sigma = sigma

    def setFirstScores(self, firstScores):
        self.firstScores = firstScores

    def setFirstShots(self, firstShots):
        self.firstShots = firstShots

    def setCurrentTeam(self, currentTeam):
        self.currentTeam = currentTeam

    def addAdditionalInfo(self, additionalInfoName, additionalInfo):
        self.additionalInfoDict[additionalInfoName] = additionalInfo

    def setAsTipperForTeam(self, team):
        self.isTipperForTeam = team


