import itertools
import math
import trueskill

BETA = 25/6
BASE_RATING = 25
BASE_DEVIATION = 25*25/3/3

# https://trueskill.org/
# todo use glicko2


def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)


def update_skills_for_single_tipoff(psd, winner_code, loser_code):
    w_og = psd[winner_code].mu
    w_mu, w_si, l_mu, l_si = _match_with_raw_nums(psd[winner_code].mu, psd[winner_code].sigma, psd[loser_code].mu, psd[loser_code].sigma)
    psd[winner_code].mu = w_mu
    psd[winner_code].sigma = w_si
    psd[loser_code].mu = l_mu
    psd[loser_code].sigma = l_si
    print("winner", winner_code, 'rating increased by', w_mu-w_og, 'to', w_mu, 'loser', loser_code, 'rating is', l_mu)
    pass


def _match_with_raw_nums(winner_mu, winner_sigma, loser_mu, loser_sigma):
        winner_rating_obj = trueskill.Rating(winner_mu, winner_sigma)
        loser_rating_obj = trueskill.Rating(loser_mu, loser_sigma)
        winner_rating_obj, loser_rating_obj = trueskill.rate_1vs1(winner_rating_obj, loser_rating_obj)
        # temp = trueskill.rate_1vs1(winner_rating_obj, loser_rating_obj)
        # winner_rating_obj = temp[0]
        # loser_rating_obj = temp[1]
        return winner_rating_obj.mu, winner_rating_obj.sigma, loser_rating_obj.mu, loser_rating_obj.sigma

# glicko properly implemented would be better to account for time drift/between seasons
# functions to use:
# Rating() <- creates rating object
# rate_1vs1() <- equivalent of a game
# quality 1vs1 <- probability of draw
# TrueSkill(draw_probability=0.1, backend=scipy). Can also set beta, sigma, mu, and tau
# tau is fixation of rating restriction. beta is distance to 76% chance of win
# ^^ set environment, we need draw prob = 0
# treskill.backends.choose_backnd = scipy
# make_as_global() on env object sets global
# setup() pass the args of Trueskill env to make work





# def win_probability_1on1(player1, player2): # todo switch generic to single player
#     delta_mu = player1.mu - player2.mu
#     sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(player1, player2))
#     size = len(player1) + len(player2)
#     denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
#     ts = trueskill.global_env()
#     return ts.cdf(delta_mu / denom)