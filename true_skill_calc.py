import itertools
import math
import trueskill

BETA = 25/6
BASE_RATING = 25
BASE_DEVIATION = 25*25/3/3

# https://trueskill.org/

def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)

def create_player_skill_dictionary():
    pass