import csv
from datetime import datetime


def recordBet(exchange: str, team: str, amount: int, odds: str, includeCurrentDate=True): #assumes this is being done on the same day as the game
    dateStr = "NA"
    path = "Data/CSV/bet_history.csv"
    if includeCurrentDate:
        date = datetime.now()
        dateStr = date.strftime("%Y-%m-%d")

    appendFile = open(path, 'a')

    with appendFile:
        csvWriter = csv.writer(appendFile)
        csvWriter.writerow({exchange, team, amount, odds, dateStr})