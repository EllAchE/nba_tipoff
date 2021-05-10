class Bankroll:
    def __init__(self, initialBankroll=5000):
        self.initialBankroll = initialBankroll
        self.bankroll = initialBankroll
        self.changes = []

    def adjustBankroll(self, change):
        self.changes.append(change)
        self.bankroll += change

    def getNetChangeMagnitude(self):
        return self.bankroll - self.initialBankroll

    def getNetChangePercentage(self):
        return (self.bankroll / self.initialBankroll - 1) * 100