import ENVIRONMENT


def tip_score_prob(tip_win_odds, tip_winner_score_odds=ENVIRONMENT.TIP_WINNER_SCORE_ODDS):
    return tip_win_odds * tip_winner_score_odds + (1-tip_win_odds) * (1-tip_winner_score_odds)