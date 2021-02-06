import itertools
import json
import math

import ENVIRONMENT
from Data_Handling import reset_prediction_summaries, create_player_skill_dictionary

import trueskill
import pandas as pd

# from Functions.Odds_Calculator import independentVarOdds

# https://trueskill.org/
# todo use glicko2
# https://github.com/sublee/glicko2/blob/master/glicko2.py
from Historical_Data.Historical_Data_Retrieval import getPlayerTeamInSeason


def runTSForSeason(season, season_csv, json_path, winning_bet_threshold=0.6):
    df = pd.read_csv(season_csv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    df['Home Mu'] = None
    df['Home Sigma'] = None
    df['Away Mu'] = None
    df['Away Sigma'] = None

    winning_bets = 0
    losing_bets = 0

    print('running for season doc', season_csv, '\n', '\n')
    col_len = len(df['Game Code'])
    i = 0

    with open(json_path) as json_file:
        psd = json.load(json_file)

    with open('../Data/prediction_summaries.json') as json_file:
        dsd = json.load(json_file)

    while i < col_len:
        if df['Home Tipper'].iloc[i] != df['Home Tipper'].iloc[i]:
            i += 1
            continue
        h_tip = df['Home Tipper'].iloc[i]
        t_winner = df['Tipoff Winner'].iloc[i]
        a_tip = df['Away Tipper'].iloc[i]
        t_win_link = df['Tipoff Winner Link'].iloc[i]
        t_lose_link = df['Tipoff Loser Link'].iloc[i]
        if t_winner == h_tip:
            h_tip_code = t_win_link[11:]
            a_tip_code = t_lose_link[11:]
        elif t_winner == a_tip:
            h_tip_code = t_lose_link[11:]
            a_tip_code = t_win_link[11:]
        else:
            raise ValueError('no match for winner')

        beforeMatchPredictions(season, psd, dsd, h_tip_code, a_tip_code, t_win_link, df['First Scoring Team'].iloc[i], winning_bet_threshold)
        home_mu, home_sigma, away_mu, away_sigma = updateDataSingleTipoff(psd, t_win_link, t_lose_link, h_tip_code, df['Full Hyperlink'].iloc[i])
        df['Home Mu'].iloc[i] = home_mu
        df['Home Sigma'].iloc[i] = home_sigma
        df['Away Mu'].iloc[i] = away_mu
        df['Away Sigma'].iloc[i] = away_sigma

        i += 1

    with open(json_path, 'w') as write_file:
        json.dump(psd, write_file)

    with open('../Data/prediction_summaries.json', 'w') as write_file:
        json.dump(dsd, write_file)

    df.to_csv(season_csv[:-4] + '-test.csv')

    return winning_bets, losing_bets


def beforeMatchPredictions(season, psd, dsd, home_p_code, away_p_code, tip_winner_code, scoring_team, winning_bet_threshold=0.6):
    # home_rating_obj = trueskill.Rating(psd[home_p_code]['mu'], psd[home_p_code]['sigma'])
    # away_rating_obj = trueskill.Rating(psd[away_p_code]['mu'], psd[away_p_code]['sigma'])
    home_odds = tipWinProb(home_p_code, away_p_code, psd=psd)
    home_p_team = getPlayerTeamInSeason(home_p_code, season, long_code=False)[0]
    away_p_team = getPlayerTeamInSeason(away_p_code, season, long_code=False)[0]

    if psd[home_p_code]['appearances'] > ENVIRONMENT.MIN_APPEARANCES and psd[away_p_code]['appearances'] > ENVIRONMENT.MIN_APPEARANCES:
        if home_odds > winning_bet_threshold:
            if tip_winner_code[11:] == home_p_code:
                dsd['correctTipoffPredictions'] += 1
                print('good prediction on home tip winner')
            else:
                dsd['incorrectTipoffPredictions'] += 1
                print('bad prediction on home tip winner')
            if home_p_team == scoring_team:
                dsd["winningBets"] += 1
                print('good prediction on home scorer')
            else:
                dsd["losingBets"] += 1
                print('bad prediction on home tip scorer')
            pass
        elif (1 - home_odds) > winning_bet_threshold:
            if tip_winner_code[11:] == away_p_code:
                dsd['correctTipoffPredictions'] += 1
                print('good prediction on away tip winner')
            else:
                dsd['incorrectTipoffPredictions'] += 1
                print('bad prediction on away tip winner')
            if away_p_team == scoring_team:
                dsd["winningBets"] += 1
                print('good prediction on away scorer')
            else:
                dsd['losingBets'] += 1
                print('bad prediction on away scorer')
        else:
            print('no bet, odds were not good enough')
    else:
        print('no bet, not enough Data on participants')


def tipWinProb(player1_code, player2_code, json_path='Data/player_skill_dictionary.json', psd=None): #win prob for first player
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
    denom = math.sqrt(size * (ENVIRONMENT.BASE_SIGMA * ENVIRONMENT.BASE_SIGMA) + sum_sigma)
    ts = trueskill.global_env()
    res = ts.cdf(delta_mu / denom)
    # print('odds', player1_code, 'beats', player2_code, 'are', res)
    return res


# def score_first_probability(player1_code, player2_code, player1_is_home, json_path=None, psd=None): #todo long term this needs to have efficiency checks
#     if psd is None:
#         with open(json_path) as json_file:
#             psd = json.load(json_file)
#
#     player1 = trueskill.Rating(psd[player1_code]["mu"], psd[player1_code]["sigma"])
#     player2 = trueskill.Rating(psd[player2_code]["mu"], psd[player2_code]["sigma"])
#     team1 = [player1]
#     team2 = [player2]
#
#     delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
#     sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
#     size = len(team1) + len(team2)
#     denom = math.sqrt(size * (ENVIRONMENT.BASE_SIGMA * ENVIRONMENT.BASE_SIGMA) + sum_sigma)
#     ts = trueskill.global_env()
#     res = ts.cdf(delta_mu / denom)
#
#     odds = res * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1-res) * (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
#     if player1_is_home:
#         odds = independentVarOdds(ENVIRONMENT.HOME_SCORE_ODDS, odds)
#
#     print('odds', player1_code, 'beats', player2_code, 'are', odds)
#     return odds


def runForAllSeasons(seasons, winning_bet_threshold=ENVIRONMENT.TIPOFF_ODDS_THRESHOLD):
    season_key = ''
    for season in seasons:
        runTSForSeason(season, '../CSV/tipoff_and_first_score_details_{}_season.csv'.format(season),
                          '../Data/player_skill_dictionary.json', winning_bet_threshold)
        season_key += str(season) + '-'

    with open('../Data/prediction_summaries.json') as pred_sum:
        dsd = json.load(pred_sum)

    dsd['seasons'] = season_key + 'with-odds-' + str(winning_bet_threshold)

    with open('../Data/prediction_summaries.json', 'w') as pred_sum:
        json.dump(dsd, pred_sum)


def updateDataSingleTipoff(psd, winner_code, loser_code, home_player_code, game_code=None):
    if game_code:
        print(game_code)
    winner_code = winner_code[11:]
    loser_code = loser_code[11:]

    w_og_mu = psd[winner_code]["mu"]
    w_og_si = psd[winner_code]["sigma"]
    l_og_mu = psd[loser_code]["mu"]
    l_og_si = psd[loser_code]["sigma"]
    w_mu, w_si, l_mu, l_si = _matchWithRawNums(psd[winner_code]["mu"], psd[winner_code]["sigma"], psd[loser_code]['mu'], psd[loser_code]["sigma"])
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

    print('Winner:', winner_code, 'rating increased', w_mu - w_og_mu, 'to', w_mu, '. Sigma is now', w_si, '. W:', w_wins, 'L', w_appearances - w_wins)
    print('Loser:', loser_code, 'rating decreased', l_mu - l_og_mu, 'to', l_mu, '. Sigma is now', l_si, '. W:', l_appearances - l_losses, 'L', l_losses)

    if home_player_code == winner_code:
        home_mu = w_og_mu
        home_sigma = w_og_si
        away_mu = l_og_mu
        away_sigma = l_og_si
    elif home_player_code == loser_code:
        home_mu = l_og_mu
        home_sigma = l_og_si
        away_mu = w_og_mu
        away_sigma = w_og_si

    return home_mu, home_sigma, away_mu, away_sigma


def _matchWithRawNums(winner_mu, winner_sigma, loser_mu, loser_sigma):
        winner_rating_obj = trueskill.Rating(winner_mu, winner_sigma)
        loser_rating_obj = trueskill.Rating(loser_mu, loser_sigma)
        winner_rating_obj, loser_rating_obj = trueskill.rate_1vs1(winner_rating_obj, loser_rating_obj)
        return winner_rating_obj.mu, winner_rating_obj.sigma, loser_rating_obj.mu, loser_rating_obj.sigma


# env = trueskill.TrueSkill(draw_probability=0, backend='scipy')
# env.make_as_global()
#
# reset_prediction_summaries() # reset sums
# create_player_skill_dictionary() # clears the stored values,
#
# sss = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
#        2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
#
# run_for_all_seasons(sss, winning_bet_threshold=ENVIRONMENT.TIPOFF_ODDS_THRESHOLD)
