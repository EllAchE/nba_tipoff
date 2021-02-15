class Season:
    def __init__(self, seasonEndYear):
        self.gameHeaders = None
        self.seasonEndYear = seasonEndYear

    def setGameHeaders(self, gameHeaders):
        self.gameHeaders = gameHeaders