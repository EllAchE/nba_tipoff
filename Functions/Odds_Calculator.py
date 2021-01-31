'''
Methods to look at betting lines and see if they are worth it
'''

import numpy as np


def solve_system_eqns_dim_5(a, b, c, d, e, amount_to_win=100):
    A = np.array(
        [[a, -1, -1, -1, -1],
         [-1, b, -1, -1, -1],
         [-1, -1, c, -1, -1],
         [-1, -1, -1, d, -1],
         [-1, -1, -1, -1, e]]
    )

    B = np.array([[amount_to_win], [amount_to_win], [amount_to_win], [amount_to_win], [amount_to_win]])

    return np.linalg.inv(A).dot(B)


def kelly_bet(loss_amt, win_odds, win_amt=1, pot_size=None): # assumes binary outcome, requires dollar value
    kelly_ratio = win_odds/loss_amt - (1-win_odds)/win_amt
    # todo refactor this to work with only loss_amt, win amt set to 1.0

    if pot_size is None:
        return kelly_ratio
    else:
        return kelly_ratio * pot_size


def win_rate_for_positive_ev(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        req_win_per = 100 / (100 + odds_num) * 100
    else:
        req_win_per = odds_num / (100 + odds_num) * 100
    print('with odds', odds_str, 'you must win', "{:.2f}".format(req_win_per) + '%')

    return req_win_per


def validate_ev():
    pass


def cost_for_100(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        return 10000/odds_num
    elif odds_str[0] == '-':
        return odds_num
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')


def cost_for_1(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        return 100/odds_num
    elif odds_str[0] == '-':
        return odds_num/100
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')



def decimal_to_american(dec_odds): # http://www.betsmart.co/odds-conversion-formulas/#americantodecimal
    if (dec_odds - 1) > 1:
        return '+' + str(100 * (dec_odds - 1))
    else:
        return '-' + str(100/(dec_odds - 1))


def american_to_decimal(american_odds):
    pass


# should be [[name, line], [name, line]]
def buy_all_players_or_one_side(player_lines, team_line): # based on preliminary numbers it's almost certainly
    total = 0
    i = 0
    costs = solve_system_eqns_dim_5(player_lines[0][1], player_lines[1][1], player_lines[2][1], player_lines[3][1], player_lines[4][1])

    for cost in costs:
        total += cost
        print('to win $100 for player', player_lines[i][0], 'will cost $' + str(cost[0]))
        i += 1
    t_cost = cost_for_100(team_line)
    total_num = total[0]
    if total_num < 100:
        total_num = 10000/total_num
        total = str('+' + str(total_num))
    else:
        total = str('-' + str(total_num))
    print()

    if t_cost > total_num:
        print("All Players, which was", total, "vs team line of", t_cost)
    else:
        print('$' + str(t_cost) + " for TEAM is a better deal than $" + str(total) + ' for its players.')


def independent_var_odds(*args):
    total_odds = args[0]/(1-args[0])
    for odds in args[1:]:
        total_odds = total_odds * odds/(1-odds)

    return total_odds/(1 + total_odds)

print(kelly_bet(1, 1.18, 0.62))


# p_lines = [['Gobert', 5.5], ['O\'Neale', 7.5], ['Bogdonavic', 7.5], ['Mitchell', 10], ['Conley', 14]]
# t_line = '-107'
# buy_all_players_or_one_side(p_lines, t_line)

# win_rate_for_positive_ev('-110')

# print()
# print(win_rate_for_positive_ev('+115'))
#
#
# solve_system_eqns_dim_5(650, 800, 1100, 1200, 1600)
