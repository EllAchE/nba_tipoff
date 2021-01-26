def win_rate_for_positive_ev(odds):
    odds_str = str(odds)
    odds_num = int(odds_str[1:])
    if odds_str[0] == '+':
        return odds_num / (100 + odds_num)
    else:
        return 100 / (100 - odds_num)
    return win_rate