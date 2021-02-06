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


def score_first_probability(player1_code, player2_code, player1_is_home, json_path=None, psd=None): #todo long term this needs to have efficiency checks
    if psd is None:
        with open(json_path) as json_file:
            psd = json.load(json_file)

    player1 = trueskill.Rating(psd[player1_code]["mu"], psd[player1_code]["sigma"])
    player2 = trueskill.Rating(psd[player2_code]["mu"], psd[player2_code]["sigma"])
    team1 = [player1]
    team2 = [player2]

    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (ENVIRONMENT.BASE_SIGMA * ENVIRONMENT.BASE_SIGMA) + sum_sigma)
    ts = trueskill.global_env()
    res = ts.cdf(delta_mu / denom)

    odds = res * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1-res) * (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
    if player1_is_home:
        odds = independentVarOdds(ENVIRONMENT.HOME_SCORE_ODDS, odds)

    print('odds', player1_code, 'beats', player2_code, 'are', odds)
    return odds


def sysEMainDiagonalVarsNeg1Fill(argsList, amt_to_win=1):
    #todo need standardized form of args
    arg_len = len(argsList)
    twod_arr = [[]] * arg_len
    i = 0

    for var in argsList:
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


def checkEvPlayerCodesOddsLine(odds, p1, p2):
    prob = getScoreProb(p1, p2)
    bet = checkEvPositive(odds, prob)
    if bet:
        print("Bet on", p1, "with odds", odds, "based on score prob", prob)
    else:
        print("don't bet")
    return prob


def getScoreProb(team_center_code, opponent_center_code):
    tip_win_odds = tipWinProb(team_center_code, opponent_center_code)
    return tipScoreProb(tip_win_odds)


# should be [[name, line], [name, line]]
def convertPlayerLinesToSingleLine(playerOddsList):
    total = 0
    i = 0
    costsAsAOdds = [playerOddsList[0]['odds'], playerOddsList[1]['odds'], playerOddsList[2]['odds'], playerOddsList[3]['odds'], playerOddsList[4]['odds']]
    costsAsRatios = map(americanToDecimal, costsAsAOdds)
    costs = sysEMainDiagonalVarsNeg1Fill(list(costsAsRatios))

    for cost in costs:
        total += cost
        print('to win', 'AMT TODO',  'for player', playerOddsList[i]['player'], 'will cost $' + str(cost))
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
