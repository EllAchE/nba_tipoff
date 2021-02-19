class Team:
    def __init__(self, teamCode, isActiveTeam=True):
        self.teamCode = teamCode
        self.currentRoster = None
        self.teamShortName = None
        self.teamFullName = None
        self.teamCity = None
        self.teamMascotName = None
        self.isActiveTeam = isActiveTeam