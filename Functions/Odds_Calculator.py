'''
Methods to look at betting lines and see if they are worth it
'''
import itertools
import json
import math

import numpy as np
import trueskill

import ENVIRONMENT
from Functions.True_Skill_Calc import tipWinProb


def scoreFirstProb(p1Code, p2Code, p1isHome, jsonPath=None, psd=None): #todo long term this needs to have efficiency checks
    if psd is None:
        with open(jsonPath) as jsonFile:
            psd = json.load(jsonFile)

    player1 = trueskill.Rating(psd[p1Code]["mu"], psd[p1Code]["sigma"])
    player2 = trueskill.Rating(psd[p2Code]["mu"], psd[p2Code]["sigma"])
    team1 = [player1]
    team2 = [player2]

    deltaMu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sumSigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (ENVIRONMENT.BASE_SIGMA * ENVIRONMENT.BASE_SIGMA) + sumSigma)
    ts = trueskill.global_env()
    res = ts.cdf(deltaMu / denom)

    odds = res * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1-res) * (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
    if p1isHome:
        odds = independentVarOdds(ENVIRONMENT.HOME_SCORE_ODDS, odds)

    print('odds', p1Code, 'beats', p2Code, 'are', odds)
    return odds


def sysEMainDiagonalVarsNeg1Fill(*args, amtToWin=1, amtToLose=None): #takes in decimal odds
    argLen = len(args)
    twoDArr = [[]] * argLen
    i = 0

    for var in args:
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


# todo add kelly_processor to format input properly
def kellyBet(lossAmt, winOdds, winAmt=1, bankroll=None): # assumes binary outcome, requires dollar value
    kellyRatio = winOdds / lossAmt - (1 - winOdds) / winAmt

    if bankroll is None:
        return kellyRatio
    else:
        return kellyRatio * bankroll


def positiveEvThresholdFromAmerican(odds):
    oddsStr = str(odds)
    oddsNum = float(oddsStr[1:])
    if oddsStr[0] == '+':
        reqWinPer = 100 / (100 + oddsNum)
    else:
        reqWinPer = oddsNum / (100 + oddsNum)
    print('with odds', oddsStr, 'you must win', "{:.2f}".format(reqWinPer) + '%')

    return reqWinPer


def costFor100(odds):
    oddsStr = str(odds)
    oddsNum = float(oddsStr[1:])
    if oddsStr[0] == '+':
        return 10000/oddsNum
    elif oddsStr[0] == '-':
        return oddsNum
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')


def getEvMultiplier(scoreProb, oddsThreshold):
    winAmt = 100/oddsThreshold - 100
    return (scoreProb * winAmt - 100 * (1 - scoreProb)) / 100


def costFor1(odds):
    oddsStr = str(odds)
    oddsNum = float(oddsStr[1:])
    if oddsStr[0] == '+':
        return 100/oddsNum
    elif oddsStr[0] == '-':
        return oddsNum/100
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')


def decimalToAmerican(decOdds): # http://www.betsmart.co/odds-conversion-formulas/#americantodecimal
    if (decOdds - 1) > 1:
        return '+' + str(100 * (decOdds - 1))
    else:
        return '-' + str(100 / (decOdds - 1))


def americanToDecimal(americanOdds):
    odds = positiveEvThresholdFromAmerican(americanOdds)
    return 1/odds


def check_for_edge(home_team, away_team, home_c, away_c, home_odds, away_odds, bankroll):
    pass


def tipScoreProb(tipWinOdds, tipWinnerScoresOdds=ENVIRONMENT.TIP_WINNER_SCORE_ODDS):
    return tipWinOdds * tipWinnerScoresOdds + (1 - tipWinOdds) * (1 - tipWinnerScoresOdds)


def kellyBetFromAOddsAndScoreProb(scoreProb, americanOdds, bankroll=ENVIRONMENT.BANKROLL):
    loss_amt = costFor1(americanOdds)
    return kellyBet(loss_amt, scoreProb, bankroll=bankroll)


def checkEvPositiveBackLayAndGetScoreProb(teamOdds, teamTipperCode, opponentTipperCode):
    minWinRate = positiveEvThresholdFromAmerican(teamOdds)
    minLossRate = 1 - minWinRate
    tipWinOdds = tipWinProb(teamTipperCode, opponentTipperCode)
    scoreProb = tipScoreProb(tipWinOdds)

    if scoreProb > minWinRate:
        print('bet on them')
        return scoreProb
    elif (1-scoreProb) > minLossRate:
        print('bet against them')
        return (1-scoreProb)
    else:
        print('don\'t bet either side')
        return None


def checkEvPositive(teamOdds, scoreProb):
    min_win_rate = positiveEvThresholdFromAmerican(teamOdds)
    if scoreProb > min_win_rate:
        return True
    else:
        return False


def checkEvPlayerCodesOddsLine(odds, p1, p2):
    prob = getScoreProb(p1, p2)
    bet = checkEvPositive(odds, prob)
    if bet:
        print("Bet on", p1, "with odds", odds, "based on score prob", prob)
    else:
        print("don't bet")
    return prob


def getScoreProb(teamTipperCode, opponentTipperCode):
    tip_win_odds = tipWinProb(teamTipperCode, opponentTipperCode)
    return tipScoreProb(tip_win_odds)


# should be [[name, line], [name, line]]
def convertPlayerLinesToSingleLine(playerOddsList):
    total = 0
    i = 0
    costs = sysEMainDiagonalVarsNeg1Fill(playerOddsList[0][1], playerOddsList[1][1], playerOddsList[2][1], playerOddsList[3][1], playerOddsList[4][1])

    for cost in costs:
        total += cost
        print('to win $100 for player', playerOddsList[i][0], 'will cost $' + str(cost[0]))
        i += 1
    totalNum = total[0]
    if totalNum < 100:
        totalNum = 10000/totalNum
        total = str('+' + str(totalNum))
    else:
        total = str('-' + str(totalNum))
    return total
    # def buyPlayersOrTeam(player_lines, team_line): # based on preliminary numbers it's almost certainly
    #     if t_cost > total_num:
    #         print("All Players, which was", total, "vs team line of", t_cost)
    #     else:
    #         print('$' + str(t_cost) + " for TEAM is a better deal than $" + str(total) + ' for its players.')


def returnGreaterOdds(odds1, odds2):
    odds1Cost = costFor100(odds1)
    odds2Cost = costFor100(odds2)
    if odds1Cost > odds2Cost:
        return odds2
    return odds1


def independentVarOdds(*args):
    totalOdds = args[0]/(1-args[0])
    for odds in args[1:]:
        totalOdds = totalOdds * odds/(1-odds)

    return totalOdds/(1 + totalOdds)


# p_lines = [['Gobert', 5.5], ['O\'Neale', 8], ['Bogdonavic', 9], ['Mitchell', 12], ['Conley', 14]]
# t_line = '-107'
# buy_all_players_or_one_side(p_lines, t_line)

# print(win_rate_for_positive_ev('-110'))
# print(win_rate_for_positive_ev('+115'))

# print(kelly_bet(1, 1.18, 0.62))
