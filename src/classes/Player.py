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
