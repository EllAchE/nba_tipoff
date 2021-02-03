import json

import pandas as pd

# todo create a probabilistic means of comparing players that does not use trueskill algo

def naive_comparison(p1):
    return 1 - weaker_player_win_rate * stronger_player_loss_rate
