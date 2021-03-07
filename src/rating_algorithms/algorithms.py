# backlogtodo test a probabilistic means of comparing players that does not use rating_algorithms algo
# todo use glicko2/compare it to rating_algorithms
# todo add time decay to glicko2/true skill RD

# todo trueskill/glicko tuning:
# lower tau prevents volatitliy from changing a lot. It's a baseline volatiity added to prevent convergence to zero by
# the standard deviation

# backlogtodo track stats on appearance first time midseason, first tip ever etc.
# https://jmlr.csail.mit.edu/papers/volume12/weng11a/weng11a.pdf
import itertools
import json
import math

import trueskill

import ENVIRONMENT


def naiveComparison(): # p1, p2):
#     return 1 - weaker_player_win_rate * stronger_player_loss_rate
    pass

def trueSkill2():
    # this would have to be recreated from scratch, based on the research, so...
    # https://www.microsoft.com/en-us/research/uploads/prod/2018/03/trueskill2.pdf
    pass

def eloDictionary():
    # https://github.com/sublee/elo
    pass

def glickoDictionary():
    # https://github.com/sublee/glicko2/blob/master/glicko2.py
    pass

def _trueSkillMatchWithRawNums(winnerMu, winnerSigma, loserMu, loserSigma):
        winnerRatingObj = trueskill.Rating(winnerMu, winnerSigma)
        loserRatingObj = trueskill.Rating(loserMu, loserSigma)
        winnerRatingObj, loserRatingObj = trueskill.rate_1vs1(winnerRatingObj, loserRatingObj)
        return winnerRatingObj.mu, winnerRatingObj.sigma, loserRatingObj.mu, loserRatingObj.sigma

def trueSkillTipWinProb(player1_code: str, player2_code: str, json_path: str = ENVIRONMENT.PLAYER_SKILL_DICT_PATH, psd: Any = None): #win prob for first player
    env = trueskill.TrueSkill(draw_probability=0, backend='scipy', tau=ENVIRONMENT.TAU)
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
    # print('odds', player1_code, 'beats', player2_code, 'are', res)
    return res

def machineLearning():
    pass
