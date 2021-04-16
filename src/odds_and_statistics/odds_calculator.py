'''
Methods to look at betting lines and see if they are worth it
'''
import json
import math
import numpy as np
import ENVIRONMENT

from typing import Any, Optional

from src.database.database_access import getUniversalPlayerName, getPlayerCurrentTeam, getUniversalTeamShortCode
from src.rating_algorithms.algorithms import trueSkillTipWinProb

# def getScoreProb(teamTipperCode: str, opponentTipperCode: str):
#     tipWinOdds = trueSkillTipWinProb(teamTipperCode, opponentTipperCode)
#     return tipScoreProb(tipWinOdds)
#
# def tipScoreProb(tipWinOdds: float, tipWinnerScoresOdds: float = ENVIRONMENT.TIP_WINNER_SCORE_ODDS):
#     return tipWinOdds * tipWinnerScoresOdds + (1 - tipWinOdds) * (1 - tipWinnerScoresOdds)

# backlogtodo allow this to toggle to different algos
from src.utils import removeAllNonLettersAndLowercase


def scoreFirstProb(p1Code: str, p2Code: str, quarter, jsonPath: Optional[str] = None, psd=None):
    if quarter == "QUARTER_2" or quarter == "QUARTER_3":
        temp = p2Code
        p2Code = p1Code
        p1Code = temp
    tWinProb = trueSkillTipWinProb(p1Code, p2Code)
    oddsWithObservedTipScore = tWinProb * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1 - tWinProb) * (1 - ENVIRONMENT.TIP_WINNER_SCORE_ODDS)

    p1 = getUniversalPlayerName(p1Code)
    t1 = getUniversalTeamShortCode(getPlayerCurrentTeam(p1))
    p2 = getUniversalPlayerName(p2Code)
    t2 = getUniversalTeamShortCode(getPlayerCurrentTeam(p2))

    with open(ENVIRONMENT.FIRST_POINT_TEAM_META.format(ENVIRONMENT.CURRENT_SEASON)) as rFile:
        metaFile = json.load(rFile)

    # todo backtest for all quarters/seasons and adjust this. This math doesn't actually make any sense
    quarterLowercased = removeAllNonLettersAndLowercase(quarter)
    reducedNaiveScoreFirstAdjustment = math.sqrt(metaFile[t1][quarterLowercased]['naiveAdjustmentFactor']) / math.sqrt(metaFile[t2][quarterLowercased]['naiveAdjustmentFactor'])
    # reducedNaiveScoreFirstAdjustment = math.sqrt(reducedNaiveScoreFirstAdjustment)
    # reducedNaiveScoreFirstAdjustment = math.sqrt(reducedNaiveScoreFirstAdjustment)

    oddsRatio = oddsWithObservedTipScore / (1-oddsWithObservedTipScore) * reducedNaiveScoreFirstAdjustment
    oddsAfterAdjustment = oddsRatio /(1+oddsRatio)

    totalOdds = oddsAfterAdjustment

    # backlogtodo the independentVarOdds is probably invalid for joint probabiilty
    # if p1isHome:
    #     odds = independentVarOdds(ENVIRONMENT.HOME_SCORE_ODDS, odds)

    # print('odds team of', p1Code, 'scores before team of', p2Code, 'are', totalOdds)
    return totalOdds

def getPlayerSpread(oddsLine, winProb: float, playerSpreadAsSingleAOdds: str):
    oddsOnly = list()
    playerSpread = list()
    numPlayers = len(oddsLine)
    lossAmt = costFor1(playerSpreadAsSingleAOdds)
    kelly = kellyBetReduced(lossAmt, winProb, bankroll=ENVIRONMENT.BANKROLL)

    for player in oddsLine:
        oddsOnly.append(americanToDecimal(player['odds']))

    bettingSpread = sysEMainDiagonalVarsNeg1Fill(oddsOnly, amtToLose=kelly)

    i = 0
    while i < numPlayers:
        playerSpread.append({"player": oddsLine[i]['player'], "bet":bettingSpread[i], "odds":oddsLine[i]["odds"]})
        i += 1

    return playerSpread


def sysEMainDiagonalVarsNeg1Fill(argsList, amtToWin: float = 1, amtToLose: Optional[float] = None): #takes in decimal odds
    argLen = len(argsList)
    twoDArr = [[]] * argLen
    i = 0

    for var in argsList:
        arr = [-1] * argLen
        arr[i] = var
        twoDArr[i] = arr
        i += 1

    A = np.array(twoDArr)
    B = np.array([amtToWin] * argLen)

    playerSpread = np.linalg.inv(A).dot(B)

    if amtToLose is None:
        return playerSpread
    else:
        cost = 0
        for amt in playerSpread:
            cost += amt

        multiplier = amtToLose/cost
        return playerSpread * multiplier

def getArbitrageRatiosTwoLines(bet1, bet2, printResult=False):
    ratios = np.array(sysEMainDiagonalVarsNeg1Fill([costFor1(bet1), costFor1(bet2)]))
    ratios = ratios / max(ratios) * 100
    if printResult:
        print('On Bet 1 ratio is', str(ratios[0]) + '.', 'For Bet 2', str(ratios[1]))
    return ratios

def checkForArbitrageAnyNumberOfLines(*args, printResult=False):
    decimalOddsArgList = list(map(americanToRatio, args))
    ratios = np.array(sysEMainDiagonalVarsNeg1Fill(decimalOddsArgList))
    if ratios[0] < 0:
        if printResult:
            print('No arbitrage')
    else:
        ratios = ratios / max(ratios) * 100
        if printResult:
            i = 0
            for line in ratios:
                i += 1
                print('For bet', i, 'ratio is', line)
        return ratios

def kellyBetReduced(lossAmt: float, winOdds: float, reductionFactor: float=ENVIRONMENT.REDUCTION_FACTOR, winAmt: float=1, bankroll: Optional[float] = None): # assumes binary outcome, requires dollar value
    # kellyRatio = (winOdds / lossAmt - (1 - winOdds) / winAmt) * 1
    kellyRatio = (winOdds - ((1 - winOdds) / (winAmt/lossAmt))) * reductionFactor

    if bankroll is None:
        return kellyRatio
    else:
        return kellyRatio * bankroll

def positiveEvThresholdFromAmerican(oddsStr: str):
    oddsNum = float(oddsStr[1:])
    
    if oddsStr[0] == '+':
        reqWinPer = 100 / (100 + oddsNum)
    else:
        reqWinPer = oddsNum / (100 + oddsNum)
    # print('with odds', oddsStr, 'you must win', "{:.2f}".format(reqWinPer) + '%')

    return reqWinPer

def costFor100(oddsStr: str):
    oddsNum = float(oddsStr[1:])
    
    if oddsStr[0] == '+':
        return 10000/oddsNum
    elif oddsStr[0] == '-':
        return oddsNum
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')

def getEvMultiplier(scoreProb: float, minWinPercentage: float):
    winAmt = 1 / minWinPercentage - 1
    return (scoreProb * winAmt - (1 - scoreProb)) + 1

def costFor1(odds: Any):
    oddsStr = str(odds)
    oddsNum = float(oddsStr[1:])
    
    if oddsStr[0] == '+':
        return 100/oddsNum
    elif oddsStr[0] == '-':
        return oddsNum/100
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')

def decimalToAmerican(decOdds: float): # http://www.betsmart.co/odds-conversion-formulas/#americantodecimal
    if (decOdds - 1) > 1:
        return '+' + str(100 * (decOdds - 1))
    else:
        return '-' + str(100 / (decOdds - 1))

def americanToRatio(x):
    return americanToDecimal(x) - 1

def americanToDecimal(americanOdds: Any):
    odds = positiveEvThresholdFromAmerican(americanOdds)
    return 1 / odds

def kellyBetFromAOddsAndScoreProb(scoreProb: float, americanOdds: str, bankroll: int=ENVIRONMENT.BANKROLL):
    loss_amt = costFor1(americanOdds)
    return kellyBetReduced(loss_amt, scoreProb, bankroll=bankroll)

def checkEvPositiveBackLayAndGetScoreProb(teamOdds: float, teamTipperCode: str, opponentTipperCode: str):
    minWinRate = positiveEvThresholdFromAmerican(teamOdds)
    minLossRate = 1 - minWinRate
    scoreProb = scoreFirstProb(teamTipperCode, opponentTipperCode)

    if scoreProb > minWinRate:
        print('bet on them')
        return scoreProb
    elif 1 - scoreProb > minLossRate:
        print('bet against them')
        return 1 - scoreProb
    else:
        print('don\'t bet either side')
        return None

def checkEvPositive(teamOdds: float, scoreProb: float):
    min_win_rate = positiveEvThresholdFromAmerican(teamOdds)
    if scoreProb > min_win_rate:
        return True
    else:
        return False

def checkEvPlayerCodesOddsLine(odds: float, p1: str, p2: str):
    prob = scoreFirstProb(p1, p2, quarter="QUARTER_1")
    bet = checkEvPositive(odds, prob)
    
    if bet:
        print("Bet on", p1, "with odds", odds, "based on score prob", prob)
    else:
        print("don't bet")
    
    return prob

# should be [[name, line], [name, line]]
def convertPlayerLinesToSingleLine(playerOddsList):
    total = 0
    i = 0
    costsAsAOdds = [playerOddsList[0]['odds'], playerOddsList[1]['odds'], playerOddsList[2]['odds'], playerOddsList[3]['odds'], playerOddsList[4]['odds']]

    costsAsRatios = map(americanToRatio, costsAsAOdds)
    costs = sysEMainDiagonalVarsNeg1Fill(list(costsAsRatios), amtToWin=100)

    for cost in costs:
        total += cost
    # print('to win $100',  'for player', playerOddsList[i]['player'], 'will cost $' + str(cost))
        i += 1
    total_num = total
    if total_num < 100:
        total_num = 10000/total_num
        total = str('+' + str(total_num))
    else:
        total = str('-' + str(total_num))
    return total
    # def buyPlayersOrTeam(player_lines, team_line): # based on preliminary numbers it's almost certainly
    #     if t_cost > total_num:
    #         print("All Players, which was", total, "vs team line of", t_cost)
    #     else:
    #         print('$' + str(t_cost) + " for TEAM is a better deal than $" + str(total) + ' for its players.')

def returnGreaterOdds(odds1: str, odds2: str):
    odds1Cost = costFor100(odds1)
    odds2Cost = costFor100(odds2)
    if odds1Cost > odds2Cost:
        return odds2
    return odds1

def independentVarOdds(*args: float):
    totalOdds = args[0]/(1-args[0])
    for odds in args[1:]:
        totalOdds = totalOdds * odds/(1-odds)
    return totalOdds/(1 + totalOdds)

def getBestOddsFromSetOfExchangeKeys(team, singleTeamOdds):
    firstLoop = True
    for key in singleTeamOdds[team].keys():
        if key == 'bovada':
            continue
        if firstLoop:
            odds = singleTeamOdds[team][key]
            firstLoop = False
            returnKey = key
        else:
            ogOdds = odds
            odds = returnGreaterOdds(odds, singleTeamOdds[team][key])
            if ogOdds != odds:
                returnKey = key
    return odds, returnKey

def checkForArbitrageInRetrievedOdds(jsonPath='tempGameOdds.json'):
    with open(jsonPath) as tempOdds:
        oddsDict = json.load(tempOdds)

    for game in oddsDict['games']:
        split = game.split(' ')
        team1 = split[0]
        team2 = split[1]

        bestTeam1Odds, exchange1 = getBestOddsFromSetOfExchangeKeys(team1, oddsDict)
        bestTeam2Odds, exchange2 = getBestOddsFromSetOfExchangeKeys(team2, oddsDict)
        try:
            ratios = getArbitrageRatiosTwoLines(bestTeam1Odds, bestTeam2Odds)

            if ratios[0] + ratios[1] > 200:
                print('arbitrage for game', game)
                print(team1, 'odds are', bestTeam1Odds, 'on exchange', exchange1, 'ratio is', ratios[1])
                print(team2, 'odds are', bestTeam2Odds, 'on exchange', exchange2, 'ratio is', ratios[0])
        except:
            print('possibly not enough odds in game', game)

# def assessAllBets(betDict):
#     oddsObjList = list()
#     for game in betDict['games']:
#         oddsObj = GameOdds(game)
#         oddsObjList.append(oddsObj)
#     oddsObjList.sort()

# p_lines = [['Gobert', 5.5], ['O\'Neale', 8], ['Bogdonavic', 9], ['Mitchell', 12], ['Conley', 14]]
# t_line = '-107'
# buy_all_players_or_one_side(p_lines, t_line)

# print(win_rate_for_positive_ev('-110'))
# print(win_rate_for_positive_ev('+115'))

# print(kelly_bet(1, 1.18, 0.62))
