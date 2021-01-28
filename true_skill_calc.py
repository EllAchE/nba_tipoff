import itertools
import json
import math
import Misc as misc
import Data_Retrieval as bball

import trueskill
import pandas as pd

BETA = 25/6
BASE_RATING = 25
BASE_DEVIATION = 25*25/3/3

# https://trueskill.org/
# todo use glicko2


def run_ts_for_season(season, season_csv, json_path, winning_bet_threshold=0.6):
    df = pd.read_csv(season_csv)
    df = df[df['Home Tipper'].notnull()] # filter invalid rows
    winning_bets = 0
    losing_bets = 0

    print('running for season doc', season_csv)
    print()
    print()
    col_len = len(df['Game Code'])
    i = 0

    with open(json_path) as json_file:
        psd = json.load(json_file)

    with open('prediction_summaries.json') as json_file:
        dsd = json.load(json_file)

    while i < col_len:
        before_match_predictions(season, psd, dsd, df['Home Tipper'].iloc[i], df['Away Tipper'].iloc[i], df['First Scoring Team'].iloc[i], winning_bet_threshold)
        update_fields_for_single_tipoff(psd, df['Tipoff Winner Link'].iloc[i], df['Tipoff Loser Link'].iloc[i], df['Full Hyperlink'].iloc[i])
        i += 1

    with open(json_path, 'w') as write_file:
        json.dump(psd, write_file)

    with open(json_path, 'w') as write_file:
        json.dump(dsd, write_file)

    return winning_bets, losing_bets


def before_match_predictions(season, psd, dsd, home_p_code, away_p_code, tip_winner_code, scoring_team, winning_bet_threshold=0.6):
    home_rating_obj = trueskill.Rating(psd[home_p_code].mu, psd[home_p_code].si) #todo need to make this work
    away_rating_obj = trueskill.Rating(psd[away_p_code].mu, psd[away_p_code].si)
    home_odds = trueskill.rate_1vs1(home_rating_obj, away_rating_obj)

    if psd[home_p_code].appearances > 30 and psd[away_p_code].appearances > 30: # todo make these params toggleable
        if home_odds > winning_bet_threshold:
            if tip_winner_code == home_p_code:
                dsd['correctTipoffPredictions'] += 1
            else:
                dsd['incorrectTipoffPredictions'] += 1
            if bball.get_player_team_in_season(season, home_p_code) == scoring_team:
                dsd["winningBets"] += 1
            else:
                dsd["losingBets"] += 1
            pass
        elif (1 - home_odds) > winning_bet_threshold:
            if tip_winner_code == away_p_code:
                dsd['correctTipoffPredictions'] += 1
            else:
                dsd['incorrectTipoffPredictions'] += 1
            if bball.get_player_team_in_season(season, away_p_code) == scoring_team:
                dsd["winningBets"] += 1
            else:
                dsd['losingBets'] += 1
        else:
            print('no bet, odds were not good enough')
    else:
        print('no bet, not enough data on participants')

        return None


def win_probability(player1_code, player2_code, json_path, psd=None): #win prob for first player
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
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = trueskill.global_env()
    res = ts.cdf(delta_mu / denom)
    print('odds', player1_code, 'beats', player2_code, 'are', res)
    return res


def run_for_all_seasons(seasons, winning_bet_threshold=0.6):
    winning_bets = 0
    losing_bets = 0
    for season in seasons:
        run_ts_for_season(season, 'CSV/tipoff_and_first_score_details_{}_season.csv'.format(season), 'player_skill_dictionary.json', winning_bet_threshold)

    print('winning bets', winning_bets)
    print('losing bets', losing_bets)
    print('wining bet percentage')


def update_fields_for_single_tipoff(psd, winner_code, loser_code, game_code=None):
    if game_code:
        print(game_code)
    winner_code = winner_code[11:]
    loser_code = loser_code[11:]
    w_og = psd[winner_code]["mu"]
    l_og = psd[loser_code]["mu"]
    w_mu, w_si, l_mu, l_si = _match_with_raw_nums(psd[winner_code]["mu"], psd[winner_code]["sigma"], psd[loser_code]['mu'], psd[loser_code]["sigma"])

    w_wins = psd[winner_code]["wins"] + 1
    w_appearances = psd[winner_code]["appearances"] + 1
    l_losses = psd[loser_code]["losses"] + 1
    l_appearances = psd[loser_code]["appearances"] + 1
    psd[winner_code]["wins"] = w_wins
    psd[winner_code]["appearances"] = w_appearances
    psd[loser_code]["losses"] = l_losses
    psd[loser_code]["appearances"] = l_appearances

    psd[winner_code]["mu"] = w_mu
    psd[winner_code]["sigma"] = w_si
    psd[loser_code]["mu"] = l_mu
    psd[loser_code]["sigma"] = l_si
    print('Winner:', winner_code, 'rating increased', w_mu - w_og, 'to', w_mu, '. Sigma is now', w_si, '. W:', w_wins, 'L', w_appearances - w_wins)
    print('Loser:', loser_code, 'rating decreased', l_mu - l_og, 'to', l_mu, '. Sigma is now', l_si, '. W:', l_appearances - l_losses, 'L', l_losses)


def _match_with_raw_nums(winner_mu, winner_sigma, loser_mu, loser_sigma):
        winner_rating_obj = trueskill.Rating(winner_mu, winner_sigma)
        loser_rating_obj = trueskill.Rating(loser_mu, loser_sigma)
        winner_rating_obj, loser_rating_obj = trueskill.rate_1vs1(winner_rating_obj, loser_rating_obj)
        return winner_rating_obj.mu, winner_rating_obj.sigma, loser_rating_obj.mu, loser_rating_obj.sigma




misc.create_player_skill_dictionary() # clears the stored values,

sss = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
       2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
run_for_all_seasons(sss, 0.5)



p = win_probability('lopezbr01.html', 'onealsh01.html', 'player_skill_dictionary.json')
print(p)
# p = win_probability('gasolpa01.html', 'duncati01.html', 'player_skill_dictionary.json')
# print(p)
# dunc mu": 26.480945325976894, "sigma": 0.9477003313108733,
# gas "gasolpa01.html": {"mu": 26.899836967663248, "sigma": 0.9777350089151755,



# env = trueskill.TrueSkill(draw_probability=0, backend='scipy')
# env.make_as_global()


# glicko properly implemented would be better to account for time drift/between seasons
# functions to use:
# Rating() <- creates rating object
# rate_1vs1() <- equivalent of a game
# quality 1vs1 <- probability of draw
# TrueSkill(draw_probability=0.1, backend=scipy). Can also set beta, sigma, mu, and tau
# tau is fixation of rating restriction. beta is distance to 76% chance of win
# ^^ set environment, we need draw prob = 0
# trueskill.backends.choose_backnd = scipy
# make_as_global() on env object sets global
# setup() pass the args of Trueskill env to make work


# def win_probability_1on1(player1, player2):
#     delta_mu = player1.mu - player2.mu
#     sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(player1, player2))
#     size = len(player1) + len(player2)
#     denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
#     ts = trueskill.global_env()
#     return ts.cdf(delta_mu / denom)