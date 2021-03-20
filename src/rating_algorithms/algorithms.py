# backlogtodo test a probabilistic means of comparing players that does not use rating_algorithms algo
# lower tau prevents volatitliy from changing a lot. It's a baseline volatiity added to prevent convergence to zero by
# the standard deviation
# for elo the toggleable parameter can be the length of the rating period(s)
# Known effect of running this from 1997 is that earlier players will have inflated ratings as they took all the early points
# then retired and took their points with them

# backlogtodo track stats on appearance first time midseason, first tip ever etc.
# https://jmlr.csail.mit.edu/papers/volume12/weng11a/weng11a.pdf
import itertools
import json
import math
from typing import Any

import trueskill
import elo

import ENVIRONMENT
from External_Libraries import glicko2

def naiveComparison(): # p1, p2):
    # return 1 - weaker_player_win_rate * stronger_player_loss_rate
    pass

def trueSkill2():
    # this would have to be recreated from scratch, based on the research, so...
    # https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf
    pass

def glickoDictionary():
    # https://github.com/sublee/glicko2/blob/master/glicko2.py
    # or try
    # https://github.com/deepy/glicko2/tree/master/glicko2
    pass

def eloDictionary():
    # https://github.com/sublee/elo
    # def expect(self, rating, other_rating): # this predicts the expected value of rating 1 over rating 2)
    # 2 * beta is the f factor for this library, which is the denominator of the diff in the ratings calculation
    # K_Factor is the K factor for sensitivity to game change. 538 for games set this to 10, should be toggled
    # def rate_1vs1(self, rating1, rating2, drawn=False): # function that can be used to return the new ratings
    pass

def glickoMatchWithRawNums(winnerMu: float, winnerSigma: float, winnerPhi: float, loserMu: float, loserSigma: float, loserPhi: float):
    ratingObj1 = glicko2.Rating(mu=winnerMu, phi=winnerPhi, sigma=winnerSigma)
    ratingObj2 = glicko2.Rating(mu=loserMu, phi=loserPhi, sigma=loserSigma)
    glickoObj = glicko2.Glicko2(tau=ENVIRONMENT.BASE_GLICKO_TAU, epsilon=ENVIRONMENT.BASE_GLICKO_EPSILON)
    newRO1, newRO2 = glickoObj.rate_1vs1(ratingObj1, ratingObj2)
    return newRO1.mu, newRO1.sigma, newRO1.phi, newRO2.mu, newRO2.sigma, newRO2.phi

# backlogtodo toggle/test the glicko, ts and elo predictions
# this is going to have to be done with histograms bucketed out to an appropriate size and a minimum
# todo switch to elo (if logloss cannot be better optimized)
def glickoTipWinProb(player1Code: str, player2Code: str, jsonPath: str = ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH, psd: Any = None): #win prob for first player
    if psd is None:
        with open(jsonPath) as json_file:
            psd = json.load(json_file)

    glickoObj = glicko2.Glicko2()
    player1 = glicko2.Rating(mu=psd[player1Code]['mu'], phi=psd[player1Code]['phi'], sigma=psd[player1Code]['sigma'])
    player2 = glicko2.Rating(mu=psd[player2Code]['mu'], phi=psd[player2Code]['phi'], sigma=psd[player2Code]['sigma'])
    return glickoObj.expect_score(player1, player2, glickoObj.reduce_impact(player1))

def glickoRatingPeriod():
    pass

# backlogtodo possibly creating a new Elo object here repeatedly is inefficient
def eloMatchWithRawNums(winnerElo: int, loserElo: int):
    eloObj = elo.Elo()
    updatedWinnerElo, updatedLoserElo = eloObj.rate_1vs1(winnerElo, loserElo)
    return updatedWinnerElo, updatedLoserElo

def _eloGlobalConstants(k:int= ENVIRONMENT.K_FACTOR, baseElo=ENVIRONMENT.BASE_ELO, beta=ENVIRONMENT.BASE_ELO_BETA):
    elo.setup(k_factor=k, initial=baseElo, beta=beta)
    print('Set k, base Elo and beta to', k, baseElo, beta)

def eloRatingPeriod(selfRating: int, gameResults: Any):
    # For this gameResults is a series ( I believe an actual pd.series) that has Score (i.e. 1, 0.5 or 0 for W/L/D) and
    # Other Rating (i.e. opponent rating) as the 2 params. Run this for x games into the season, perhaps when first team
    # reaches 30, then go game by game for a season.
    # For porting to a new season you want some continuity; i.e. 2/3 of the previous elo value. Or leave it the same.
    # pass
    pass

def eloTipWinProb(player1Code: str, player2Code: str, jsonPath: str = ENVIRONMENT.PLAYER_ELO_DICT_PATH, psd: Any = None): #win prob for first player
    if psd is None:
        with open(jsonPath) as json_file:
            psd = json.load(json_file)
    elo1 = psd[player1Code]['elo']
    elo2 = psd[player2Code]['elo']
    eloObj = elo.Elo()
    return eloObj.expect(elo1, elo2)

def trueSkillMatchWithRawNums(winnerMu: float, winnerSigma: float, loserMu: float, loserSigma: float):
        winnerRatingObj = trueskill.Rating(winnerMu, winnerSigma)
        loserRatingObj = trueskill.Rating(loserMu, loserSigma)
        winnerRatingObj, loserRatingObj = trueskill.rate_1vs1(winnerRatingObj, loserRatingObj)
        return winnerRatingObj.mu, winnerRatingObj.sigma, loserRatingObj.mu, loserRatingObj.sigma

def trueSkillTipWinProb(player1Code: str, player2Code: str, psd=None): #win prob for first player
    env = trueskill.TrueSkill(draw_probability=0, backend='scipy', tau=ENVIRONMENT.BASE_TS_TAU, beta=ENVIRONMENT.BASE_TS_BETA)
    env.make_as_global()
    if psd is None:
        with open(ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH) as json_file:
            psd = json.load(json_file)

    player1 = trueskill.Rating(psd[player1Code]['mu'], psd[player1Code]['sigma'])
    player2 = trueskill.Rating(psd[player2Code]['mu'], psd[player2Code]['sigma'])
    team1 = [player1]
    team2 = [player2]

    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (ENVIRONMENT.BASE_TS_BETA * ENVIRONMENT.BASE_TS_BETA) + sum_sigma)
    ts = trueskill.global_env()
    res = ts.cdf(delta_mu / denom)
    # print('odds', player1_code, 'beats', player2_code, 'are', res)
    return res

def machineLearning():
    pass
