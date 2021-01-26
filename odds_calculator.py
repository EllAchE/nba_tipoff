'''
Methods to look at betting lines and see if they are worth it
'''


def win_rate_for_positive_ev(odds):
    odds_str = str(odds)
    odds_num = int(odds_str[1:])
    if odds_str[0] == '+':
        return odds_num / (100 + odds_num)
    else:
        return 100 / (100 - odds_num)


def cost_for_100(odds):
    odds_str = str(odds)
    odds_num = int(odds_str[1:])
    if odds_str[0] == '+':
        return 10000/odds_num
    elif odds_str[0] == '-':
        return odds_num
    else:
        raise ValueError('not proper line')


# should be [[name, line], [name, line]]
def buy_all_players_or_one_side(player_lines, team_line):
    player_cost_for_100 = list()
    total = 0
    for line in player_lines:
        cost = cost_for_100(line[1])
        player_cost_for_100.append([line[0], cost])
        total += cost
        print(line, cost)

    t_cost = cost_for_100(team_line)
    if t_cost > total:
        return ["All Players, which was", total, "vs team line of", t_cost]
    else:
        return ["Team, which was", t_cost, "vs player cost of", total]

p_lines = [['a', '+600'], ['b', '+600'], ['c', '+700'], ['d', '+900'], ['e', '+1400']]
t_line = '-112'
print(buy_all_players_or_one_side(p_lines, t_line))