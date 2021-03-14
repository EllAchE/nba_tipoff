import csv
from datetime import datetime

# 1) record bet data that are placed
# 2) take the odds even if bets aren't placed
import ENVIRONMENT
#backlogtodo this should be archived as it won't be needed unles a site doesn't offer retroactive vie of your bet history

def recordBet(exchange: str, team: str, amount: int, odds: str, includeCurrentDate=True): #assumes this is being done on the same day as the game
    dateStr = "NA"
    if includeCurrentDate:
        date = datetime.now()
        dateStr = date.strftime("%Y-%m-%d")

    appendFile = open(ENVIRONMENT.BET_HISTORY_PATH, 'a')

    with appendFile:
        csvWriter = csv.writer(appendFile)
        csvWriter.writerow({exchange, team, amount, odds, dateStr})