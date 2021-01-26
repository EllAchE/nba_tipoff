import itertools
import json
import math
import trueskill
import pandas as pd
import Misc as misc

BETA = 25/6
BASE_RATING = 25
BASE_DEVIATION = 25*25/3/3

# https://trueskill.org/
# todo use glicko2


def run_ts_for_season(season_csv):
    df = pd.read_csv(season_csv)
    df = df[df['Home Tipper'].notnull()] # filter invalid rows
    print('running for season doc', season_csv)
    print()
    print()
    col_len = len(df['Game Code'])
    i = 0

    with open('player_skill_dictionary.json') as json_file:
        psd = json.load(json_file)
    while i < col_len:
        update_fields_for_single_tipoff(psd, df['Tipoff Winner Link'].iloc[i], df['Tipoff Loser Link'].iloc[i])
        i += 1

    with open('player_skill_dictionary.json', 'w') as write_file:
        json.dump(psd, write_file)


def win_probability(player1_code, player2_code, psd=None): #win prob for first player
    if psd is None:
        with open('player_skill_dictionary.json') as json_file:
            psd = json.load(json_file)
    player1 = trueskill.Rating(psd[player1_code]["mu"], psd[player1_code]["sigma"])
    player2 = trueskill.Rating(psd[player2_code]["mu"], psd[player2_code]["sigma"])
    team1 = [player1]
    team2 = [player2]

    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)


def update_fields_for_single_tipoff(psd, winner_code, loser_code):
    print(winner_code)
    winner_code = winner_code[11:]
    loser_code = loser_code[11:]
    w_og = psd[winner_code]["mu"]
    l_og = psd[winner_code]["mu"]
    w_mu, w_si, l_mu, l_si = _match_with_raw_nums(psd[winner_code]["mu"], psd[winner_code]["sigma"], psd[loser_code]['mu'], psd[loser_code]["sigma"])

    w_wins = psd[winner_code]["wins"]
    w_appearances = psd[winner_code]["appearances"]
    l_losses = psd[loser_code]["losses"]
    l_appearances = psd[loser_code]["appearances"]
    psd[winner_code]["wins"] = w_wins + 1
    psd[winner_code]["appearances"] = w_appearances + 1
    psd[loser_code]["losses"] = l_losses + 1
    psd[loser_code]["appearances"] = l_appearances + 1

    psd[winner_code]["mu"] = w_mu
    psd[winner_code]["sigma"] = w_si
    psd[loser_code]["mu"] = l_mu
    psd[loser_code]["sigma"] = l_si
    print('Winner:', winner_code, 'rating increased', w_mu - w_og, 'to', w_mu, '. Sigma is now', w_si, '. W:', w_wins, 'L', w_appearances - w_wins)
    print('Loser:', loser_code, 'rating decreased', l_mu - l_og, 'to', l_mu, '. Sigma is now', l_si, '. W:', l_appearances - l_losses, 'L', l_losses)
    pass


def _match_with_raw_nums(winner_mu, winner_sigma, loser_mu, loser_sigma):
        winner_rating_obj = trueskill.Rating(winner_mu, winner_sigma)
        loser_rating_obj = trueskill.Rating(loser_mu, loser_sigma)
        winner_rating_obj, loser_rating_obj = trueskill.rate_1vs1(winner_rating_obj, loser_rating_obj)
        return winner_rating_obj.mu, winner_rating_obj.sigma, loser_rating_obj.mu, loser_rating_obj.sigma

misc.create_player_skill_dictionary() # clears the stored values,
run_ts_for_season('tipoff_and_first_score_details_2008_season.csv')
# p = win_probability('onealsh01.html', 'millebr01.html')
# print(p)


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