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

    X = np.linalg.inv(A).dot(B)
    return X


def win_rate_for_positive_ev(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        req_win_per = 100 / (100 + odds_num) * 100
    else:
        req_win_per = odds_num / (100 + odds_num) * 100
    print('with odds', odds_str, 'you must win', "{:.2f}".format(req_win_per) + '%')

    return req_win_per


def cost_for_100(odds):
    odds_str = str(odds)
    odds_num = float(odds_str[1:])
    if odds_str[0] == '+':
        return 10000/odds_num
    elif odds_str[0] == '-':
        return odds_num
    else:
        raise ValueError('Odds line is improperly formatted, include the + or -.')


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
        return ["All Players, which was", total, "vs team line of", t_cost]
    else:
        return '$' + str(t_cost) + " for TEAM is a better deal than $" + str(total[0]) + ' for its players.'

p_lines = [['Gobert', 6], ['O\'Neale', 10], ['Bogdonavic', 10], ['Mitchell', 12], ['Conley', 12]]
t_line = '-107'
print(buy_all_players_or_one_side(p_lines, t_line))
print()
print(win_rate_for_positive_ev('+115'))


solve_system_eqns_dim_5(650, 800, 1100, 1200, 1600)