import ENVIRONMENT
from src.database.database_creation import createPlayerGlickoDictionary
from src.rating_algorithms.algorithms import glickoTipWinProb, glickoMatchWithRawNums
# https://github.com/ryankirkman/pyglicko2/blob/master/glicko2.py
from src.rating_algorithms.common_data_processing import beforeMatchPredictions,runAlgoForSeason, runAlgoForAllSeasons


def runGlickoForSeason(season: str, seasonCsv: str, winningBetThreshold: float=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False):
    runAlgoForSeason(season, seasonCsv, ENVIRONMENT.PLAYER_GLICKO_DICT_PATH, ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH, glickoBeforeMatchPredictions,
                    glickoUpdateDataSingleTipoff, winningBetThreshold, columnAdds=['Home Glicko Mu', 'Away Glicko Mu', "Home Glicko Sigma", "Away Glicko Sigma", "Home Glicko Phi", "Away Glicko Phi"], startFromBeginning=startFromBeginning)

def glickoBeforeMatchPredictions(psd, hTipCode, aTipCode, hTeam, aTeam, tipWinCode, scoringTeam, predictionArray, actualArray, histogramPredictionsDict, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD):
    return beforeMatchPredictions(psd, hTipCode, aTipCode, hTeam, aTeam, tipWinCode, scoringTeam, predictionArray, actualArray, histogramPredictionsDict, predictionSummaryPath=ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH,
                                  minimumTipWinPercentage=winningBetThreshold, predictionFunction=glickoTipWinProb, minimumAppearances=ENVIRONMENT.MIN_GLICKO_APPEARANCES)

def runGlickoForAllSeasons(seasons, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD):
    runAlgoForAllSeasons(seasons, ENVIRONMENT.PLAYER_GLICKO_DICT_PATH, ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH, glickoBeforeMatchPredictions,
                         glickoUpdateDataSingleTipoff, winningBetThreshold, columnAdds=['Home Glicko Mu', 'Away Glicko Mu', "Home Glicko Sigma", "Away Glicko Sigma", "Home Glicko Phi", "Away Glicko Phi"])

def glickoUpdateDataSingleTipoff(psd, winnerCode, loserCode, homePlayerCode, game_code=None):
    if game_code:
        print(game_code)
    winnerCode = winnerCode[11:]
    loserCode = loserCode[11:]

    winnerOgMu = psd[winnerCode]['mu']
    winnerOgSigma = psd[winnerCode]['sigma']
    winnerOgPhi = psd[winnerCode]['phi']
    loserOgMu = psd[loserCode]['mu']
    loserOgSigma = psd[loserCode]['sigma']
    loserOgPhi = psd[loserCode]['phi']
    winnerMu, winnerSigma, winnerPhi, loserMu, loserSigma, loserPhi = glickoMatchWithRawNums(winnerOgMu, winnerOgSigma, winnerOgPhi,
                                                                    loserOgMu, loserOgSigma, loserOgPhi)
    winnerWinCount = psd[winnerCode]['wins'] + 1
    winnerAppearances = psd[winnerCode]['appearances'] + 1
    loserLosses = psd[loserCode]['losses'] + 1
    loserAppearances = psd[loserCode]['appearances'] + 1

    psd[winnerCode]['wins'] = winnerWinCount
    psd[winnerCode]['appearances'] = winnerAppearances
    psd[loserCode]['losses'] = loserLosses
    psd[loserCode]['appearances'] = loserAppearances
    psd[winnerCode]['mu'] = winnerMu
    psd[winnerCode]['sigma'] = winnerSigma
    psd[winnerCode]['phi'] = winnerPhi
    psd[loserCode]['mu'] = loserMu
    psd[loserCode]['sigma'] = loserSigma
    psd[loserCode]['phi'] = loserPhi

    print('Winner:', winnerCode, 'glicko increased', winnerMu - winnerOgMu, 'to', winnerMu, '. Sigma is now', winnerSigma, '. Phi is now', winnerPhi, '. W:', winnerWinCount, 'L', winnerAppearances - winnerWinCount)
    print('Loser:', loserCode, 'glicko decreased', loserMu - loserOgMu, 'to', loserMu, '. Sigma is now', loserSigma, '. Phi is now', loserPhi,  '. W:', loserAppearances - loserLosses, 'L', loserLosses)

    if homePlayerCode == winnerCode:
        homeMu = winnerOgMu
        homeSigma = winnerOgSigma
        awayMu = loserOgMu
        awaySigma = loserOgSigma
        homePhi = winnerOgPhi
        awayPhi = loserOgPhi
    elif homePlayerCode == loserCode:
        homeMu = loserOgMu
        homeSigma = loserOgSigma
        awayMu = winnerOgMu
        awaySigma = winnerOgSigma
        homePhi = loserOgPhi
        awayPhi = winnerOgPhi

    return {'Home Glicko Mu': homeMu, 'Away Glicko Mu': awayMu, "Home Glicko Sigma": homeSigma, "Away Glicko Sigma": awaySigma,
            "Home Glicko Phi": homePhi, "Away Glicko Phi": awayPhi}

def calculateGlickoDictionaryFromZero():
    createPlayerGlickoDictionary() # clears the stored values,
    runGlickoForAllSeasons(ENVIRONMENT.ALL_SEASONS_LIST, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD)
    print('\n', 'glicko dictionary updated for seasons', ENVIRONMENT.ALL_SEASONS_LIST, '\n')

def updateGlickoDictionaryFromLastGame():
    runGlickoForSeason(ENVIRONMENT.CURRENT_SEASON, ENVIRONMENT.CURRENT_SEASON_CSV, ENVIRONMENT.PLAYER_GLICKO_DICT_PATH, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False)
    print('\n', 'glicko dictionary updated from last game', '\n')
