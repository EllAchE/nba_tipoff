import json

import numpy
from sklearn.metrics import log_loss
import pandas as pd

import ENVIRONMENT
from src.classes.Bankroll import Bankroll
from src.database.database_access import getUniversalTeamShortCode
from src.odds.odds_calculator import kellyBetFromAOddsAndScoreProb, tipoffNaiveOdds, americanToDecimal, \
    checkMinEvThreshold, americanToRatio, americanOddsPayoutForWin
from src.skill_algorithms.algorithms import trueSkillTipWinFromMuAndSigma
from src.utils import getDashDateAndHomeCodeFromGameCode


def customEvaluationMetrics(predictions, yTest):
    lenPred = len(predictions)
    totalMiss = 0
    expectedTotal = 0
    actualTotal = 0
    for i in range(0, lenPred-1):
        if yTest.iloc[i] == 1:
            totalMiss += 1 - predictions[i][1]
        elif yTest.iloc[i] == 0:
            totalMiss += predictions[i][0]
        else:
            raise ValueError("DDD")
        actualTotal += yTest.iloc[i]
        expectedTotal += predictions[i][1]

    logLoss = log_loss(yTest, predictions)

    print("Difference", totalMiss/lenPred)
    print('Expected', expectedTotal)
    print('Actual', actualTotal)
    print('bias?', expectedTotal/actualTotal)
    print("logLoss is", logLoss)

def checkBet(row, bankroll):
    homeTipWinProb = trueSkillTipWinFromMuAndSigma(player1Mu=row['Home TS Mu'], player1Sigma=row['Home TS Sigma'], player2Mu=row['Away TS Mu'], player2Sigma=row['Away TS Sigma'])
    awayTipWinProb = 1 - homeTipWinProb
    homeScoreProb = tipoffNaiveOdds(homeTipWinProb)
    awayScoreProb = tipoffNaiveOdds(awayTipWinProb)

    homeOdds = row['bestHomeOdds']
    awayOdds = row['bestAwayOdds']
    firstScorer = row['First Scoring Team']

    betHome = checkMinEvThreshold(homeScoreProb, homeOdds)
    betAway = checkMinEvThreshold(awayScoreProb, awayOdds)

    if not betAway and not betHome:
        return bankroll

    homeScores = True if getUniversalTeamShortCode(firstScorer) == getUniversalTeamShortCode(row['Home Short']) else False

    if betHome:
        homeKelly = kellyBetFromAOddsAndScoreProb(homeScoreProb, americanOdds=homeOdds, bankroll=bankroll.bankroll)
        if homeKelly > 0:
            chg = evaluateBetNetChange(homeOdds, homeScores, homeKelly)
            print('betting', homeKelly, 'on', row['Home Short'], 'in game', row['Game Code'], 'Result was', chg)
            bankroll.adjustBankroll(chg)
    if betAway:
        awayKelly = kellyBetFromAOddsAndScoreProb(awayScoreProb, americanOdds=awayOdds, bankroll=bankroll.bankroll)
        if awayKelly > 0:
            chg = evaluateBetNetChange(awayOdds, not homeScores, awayKelly)
            print('betting', awayKelly, 'on', row['Away Short'], 'in game', row['Game Code'], 'Result was', chg)
            bankroll.adjustBankroll(chg)

    return bankroll

def seasonBetRecord(historicalDataPath):
    # bet threshold
    # positive EV only
    # minimum appearances by tipper
    # using team metadata
    # purely tip win prob and no ev
    # minimum team appearances
    historicalOddsDf = pd.read_csv(historicalDataPath)
    bankroll = Bankroll()

    cols = ['fanduelHomeOdds', 'draftkingsHomeOdds', 'mgmHomeOdds', 'fanduelAwayOdds', 'draftkingsAwayOdds', 'mgmAwayOdds']
    for i in historicalOddsDf.index:
        row = historicalOddsDf.iloc[i]
        print('current bankroll', bankroll.bankroll, row['Game Code'], row['Home Short'], 'vs', row['Away Short'])
        for label in cols:
            if numpy.isnan(row[label]):
                match = False
            else:
                match = True
                break
        if match: # assumes odds for one = odds for both
            bankroll = checkBet(row, bankroll) # todo add values to the dataframe
    return bankroll

def evaluateBetNetChange(americanOdds, isWon, betAmount):
    if not isWon:
        return -1 * betAmount

    return americanOddsPayoutForWin(americanOdds, betAmount)

def createDailyMetaDict2021():
    with open(ENVIRONMENT.FIRST_FG_SUMMARY_UNFORMATTED_PATH.format(2021)) as rFile:
        firstFgDict = json.load(rFile)

    dailyDict = {}
    for game in firstFgDict:
        date, team = getDashDateAndHomeCodeFromGameCode(game['gameCode'])
        if date not in dailyDict.keys():
            dailyDict[date] = {}

