'''
Methods to look at betting lines and see if they are worth it
'''

import numpy as np

import ENVIRONMENT
from Classes.GameOdds import GameOdds
from Functions.True_Skill_Calc import tipWinProb


def sysEMainDiagonalVarsNeg1Fill(*args, amt_to_win=1):
    arg_len = len(args)
    twod_arr = [[]] * arg_len
    i = 0

    for var in args:
        arr = [-1] * arg_len
        arr[i] = var
        twod_arr[i] = arr
        i += 1

    A = np.array(twod_arr)
    B = np.array([amt_to_win] * arg_len)

    return np.linalg.inv(A).dot(B)


# todo add kelly_processor to format input properly
def kellyBet(loss_amt, win_odds, win_amt=1, bankroll=None): # assumes binary outcome, requires dollar value
    kelly_ratio = win_odds/loss_amt - (1-win_odds)/win_amt

    if bankroll is None:
        return kelly_ratio
    else:
        return kelly_ratio * bankroll


def positiveEvThresholdFromAmerican(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        req_win_per = 100 / (100 + odds_num)
    else:
        req_win_per = odds_num / (100 + odds_num)
    print('with odds', odds_str, 'you must win', "{:.2f}".format(req_win_per) + '%')

    return req_win_per


def costFor100(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        return 10000/odds_num
    elif odds_str[0] == '-':
        return odds_num
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')


def getEvMultiplier(scoreProb, oddsThreshold):
    winAmt = 100/oddsThreshold - 100
    return (scoreProb * winAmt - 100 * (1 - scoreProb)) / 100


def costFor1(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        return 100/odds_num
    elif odds_str[0] == '-':
        return odds_num/100
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')


def decimalToAmerican(dec_odds): # http://www.betsmart.co/odds-conversion-formulas/#americantodecimal
    if (dec_odds - 1) > 1:
        return '+' + str(100 * (dec_odds - 1))
    else:
        return '-' + str(100/(dec_odds - 1))


def americanToDecimal(american_odds):
    odds = positiveEvThresholdFromAmerican(american_odds)
    return 1/odds


def check_for_edge(home_team, away_team, home_c, away_c, home_odds, away_odds, bankroll):
    pass


def tipScoreProb(tip_win_odds, tip_winner_score_odds=ENVIRONMENT.TIP_WINNER_SCORE_ODDS):
    return tip_win_odds * tip_winner_score_odds + (1-tip_win_odds) * (1-tip_winner_score_odds)


def kellyBetFromAOddsAndScoreProb(score_prob, american_odds, bankroll=ENVIRONMENT.BANKROLL):
    loss_amt = costFor1(american_odds)
    return kellyBet(loss_amt, score_prob, bankroll=bankroll)


def checkEvPositiveBackLayAndGetScoreProb(team_odds, team_center_code, opponent_center_code):
    min_win_rate = positiveEvThresholdFromAmerican(team_odds)
    min_loss_rate = 1 - min_win_rate
    tip_win_odds = tipWinProb(team_center_code, opponent_center_code)
    score_prob = tipScoreProb(tip_win_odds)

    if score_prob > min_win_rate:
        print('bet on them')
        return score_prob
    elif (1-score_prob) > min_loss_rate:
        print('bet against them')
        return (1-score_prob)
    else:
        print('don\'t bet either side')
        return None


def checkEvPositive(teamOdds, scoreProb):
    min_win_rate = positiveEvThresholdFromAmerican(teamOdds)
    if scoreProb > min_win_rate:
        return True
    else:
        return False


def getScoreProb(team_center_code, opponent_center_code):
    tip_win_odds = tipWinProb(team_center_code, opponent_center_code)
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
    total_num = total[0]
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


def returnGreaterOdds(odds1, odds2):
    odds1Cost = costFor100(odds1)
    odds2Cost = costFor100(odds2)
    if odds1Cost > odds2Cost:
        return odds2
    return odds1


def independentVarOdds(*args):
    total_odds = args[0]/(1-args[0])
    for odds in args[1:]:
        total_odds = total_odds * odds/(1-odds)

    return total_odds/(1 + total_odds)


def assessSingleBet(GameOddsObj):
    pass


def assessAllBets(betDict):
    oddsObjList = list()
    for game in betDict['games']:
        oddsObj = GameOdds(game)
        oddsObjList.append(assessSingleBet(oddsObj))


# p_lines = [['Gobert', 5.5], ['O\'Neale', 8], ['Bogdonavic', 9], ['Mitchell', 12], ['Conley', 14]]
# t_line = '-107'
# buy_all_players_or_one_side(p_lines, t_line)

# print(win_rate_for_positive_ev('-110'))
# print(win_rate_for_positive_ev('+115'))

# print(kelly_bet(1, 1.18, 0.62))
