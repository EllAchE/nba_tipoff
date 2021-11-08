class Bankroll:
    def __init__(self, initialBankroll=5000, maxBet=20000):
        self.initialBankroll = initialBankroll
        self.bankroll = initialBankroll
        self.changes = []
        self.maxBet = maxBet
        self.exchangeAllocations = {}
        # self.fanduelAllocation = 0
        # self.draftkingsAllocation = 0
        # self.mgmAllocation = 0

    def adjustBankroll(self, change):
        self.changes.append(change)
        self.bankroll += change

    def getNetChangeMagnitude(self):
        return self.bankroll - self.initialBankroll

    def getNetChangePercentage(self):
        return (self.bankroll / self.initialBankroll - 1) * 100

