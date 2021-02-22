import itertools
import json
import math
from typing import Any

import ENVIRONMENT

import trueskill
import pandas as pd

from src.classes.Player import Player
from src.functions.database_access import getUniversalPlayerName
from src.functions.database_creation import resetPredictionSummaries, createPlayerSkillDictionary
from src.historical_data.historical_data_retrieval import getPlayerTeamInSeasonFromBballRefLink
# https://github.com/sublee/glicko2/blob/master/glicko2.py


def runTSForSeason(season: str, season_csv: str, json_path: str, winning_bet_threshold: float =0.6):
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

    with open(ENVIRONMENT.PREDICTION_SUMMARIES_PATH) as json_file:
        dsd = json.load(json_file)

    while i < col_len:
        if df['Home Tipper'].iloc[i] != df['Home Tipper'].iloc[i]:
            i += 1
            continue
        hTip = df['Home Tipper'].iloc[i]
        tWinner = df['Tipoff Winner'].iloc[i]
        aTip = df['Away Tipper'].iloc[i]
        tWinLink = df['Tipoff Winner Link'].iloc[i]
        tLoseLink = df['Tipoff Loser Link'].iloc[i]
        if tWinner == hTip:
            hTipCode = tWinLink[11:]
            aTipCode = tLoseLink[11:]
        elif tWinner == aTip:
            hTipCode = tLoseLink[11:]
            aTipCode = tWinLink[11:]
        else:
            raise ValueError('no match for winner')

        beforeMatchPredictions(season, psd, dsd, hTipCode, aTipCode, tWinLink, df['First Scoring Team'].iloc[i], winning_bet_threshold)
        homeMu, homeSigma, awayMu, awaySigma = updateDataSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])
        df['Home Mu'].iloc[i] = homeMu
        df['Home Sigma'].iloc[i] = homeSigma
        df['Away Mu'].iloc[i] = awayMu
        df['Away Sigma'].iloc[i] = awaySigma

        i += 1

    with open(json_path, 'w') as write_file:
        json.dump(psd, write_file)

    with open(ENVIRONMENT.PREDICTION_SUMMARIES_PATH, 'w') as write_file:
        json.dump(dsd, write_file)

    df.to_csv(season_csv[:-4] + '-test.csv')

    return winning_bets, losing_bets


# todo setup odds prediction to use Ev or win prob rather than bet threshold
def beforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold=0.6):
    homeOdds = tipWinProb(homePlayerCode, awayPlayerCode, psd=psd)
    homePlayerTeam = getPlayerTeamInSeasonFromBballRefLink(homePlayerCode, season, longCode=False)[0]
    awayPlayerTeam = getPlayerTeamInSeasonFromBballRefLink(awayPlayerCode, season, longCode=False)[0]

    if psd[homePlayerCode]['appearances'] > ENVIRONMENT.MIN_APPEARANCES and psd[awayPlayerCode]['appearances'] > ENVIRONMENT.MIN_APPEARANCES:
        if homeOdds > winningBetThreshold:
            if tipWinnerCode[11:] == homePlayerCode:
                dsd['correctTipoffPredictions'] += 1
                print('good prediction on home tip winner')
            else:
                dsd['incorrectTipoffPredictions'] += 1
                print('bad prediction on home tip winner')
            if homePlayerTeam == scoringTeam:
                dsd["winningBets"] += 1
                print('good prediction on home scorer')
            else:
                dsd["losingBets"] += 1
                print('bad prediction on home tip scorer')
            pass
        elif (1 - homeOdds) > winningBetThreshold:
            if tipWinnerCode[11:] == awayPlayerCode:
                dsd['correctTipoffPredictions'] += 1
                print('good prediction on away tip winner')
            else:
                dsd['incorrectTipoffPredictions'] += 1
                print('bad prediction on away tip winner')
            if awayPlayerTeam == scoringTeam:
                dsd["winningBets"] += 1
                print('good prediction on away scorer')
            else:
                dsd['losingBets'] += 1
                print('bad prediction on away scorer')
        else:
            print('no bet, odds were not good enough')
    else:
        print('no bet, not enough Data on participants')

def tipWinProb(player1_code: str, player2_code: str, json_path: str = 'Data/JSON/player_skill_dictionary.json', psd: Any = None): #win prob for first player
    env = trueskill.TrueSkill(draw_probability=0, backend='scipy')
    env.make_as_global()
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
    print('odds', player1_code, 'beats', player2_code, 'are', res)
    return res


def runForAllSeasons(seasons, winning_bet_threshold=ENVIRONMENT.TIPOFF_ODDS_THRESHOLD):
    seasonKey = ''
    for season in seasons:
        runTSForSeason(season, ENVIRONMENT.SEASON_CSV_NEEDING_FORMAT_PATH.format(season),
                       ENVIRONMENT.PLAYER_SKILL_DICT_PATH, winning_bet_threshold)
        seasonKey += str(season) + '-'

    with open(ENVIRONMENT.PREDICTION_SUMMARIES_PATH) as predSum:
        dsd = json.load(predSum)

    dsd['seasons'] = seasonKey + 'with-odds-' + str(winning_bet_threshold)

    with open(ENVIRONMENT.PREDICTION_SUMMARIES_PATH, 'w') as predSum:
        json.dump(dsd, predSum)


def updateDataSingleTipoff(psd, winnerCode, loserCode, homePlayerCode, game_code=None):
    if game_code:
        print(game_code)
    winnerCode = winnerCode[11:]
    loserCode = loserCode[11:]

    winnerOgMu = psd[winnerCode]["mu"]
    winnerOgSigma = psd[winnerCode]["sigma"]
    loserOgMu = psd[loserCode]["mu"]
    loserOgSigma = psd[loserCode]["sigma"]
    winnerMu, winnerSigma, loserMu, loserSigma = _matchWithRawNums(psd[winnerCode]["mu"], psd[winnerCode]["sigma"], psd[loserCode]['mu'], psd[loserCode]["sigma"])
    winnerWinCount = psd[winnerCode]["wins"] + 1
    winnerAppearances = psd[winnerCode]["appearances"] + 1
    loserLosses = psd[loserCode]["losses"] + 1
    loserAppearances = psd[loserCode]["appearances"] + 1

    psd[winnerCode]["wins"] = winnerWinCount
    psd[winnerCode]["appearances"] = winnerAppearances
    psd[loserCode]["losses"] = loserLosses
    psd[loserCode]["appearances"] = loserAppearances
    psd[winnerCode]["mu"] = winnerMu
    psd[winnerCode]["sigma"] = winnerSigma
    psd[loserCode]["mu"] = loserMu
    psd[loserCode]["sigma"] = loserSigma

    print('Winner:', winnerCode, 'rating increased', winnerMu - winnerOgMu, 'to', winnerMu, '. Sigma is now', winnerSigma, '. W:', winnerWinCount, 'L', winnerAppearances - winnerWinCount)
    print('Loser:', loserCode, 'rating decreased', loserMu - loserOgMu, 'to', loserMu, '. Sigma is now', loserSigma, '. W:', loserAppearances - loserLosses, 'L', loserLosses)

    if homePlayerCode == winnerCode:
        homeMu = winnerOgMu
        homeSigma = winnerOgSigma
        awayMu = loserOgMu
        awaySigma = loserOgSigma
    elif homePlayerCode == loserCode:
        homeMu = loserOgMu
        homeSigma = loserOgSigma
        awayMu = winnerOgMu
        awaySigma = winnerOgSigma

    return homeMu, homeSigma, awayMu, awaySigma


def _matchWithRawNums(winnerMu, winnerSigma, loserMu, loserSigma):
        winnerRatingObj = trueskill.Rating(winnerMu, winnerSigma)
        loserRatingObj = trueskill.Rating(loserMu, loserSigma)
        winnerRatingObj, loserRatingObj = trueskill.rate_1vs1(winnerRatingObj, loserRatingObj)
        return winnerRatingObj.mu, winnerRatingObj.sigma, loserRatingObj.mu, loserRatingObj.sigma


def updateSkillDictionary():
    resetPredictionSummaries() # reset sums
    createPlayerSkillDictionary() # clears the stored values,
    runForAllSeasons(ENVIRONMENT.SEASONS_LIST, winning_bet_threshold=ENVIRONMENT.TIPOFF_ODDS_THRESHOLD)
    print("\n", "skill dictionary updated", "\n")
