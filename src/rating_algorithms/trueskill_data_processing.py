import ENVIRONMENT

from src.database.database_creation import createPlayerTrueSkillDictionary
from src.rating_algorithms.algorithms import trueSkillMatchWithRawNums, trueSkillTipWinProb
from src.rating_algorithms.common_data_processing import beforeMatchPredictions, runAlgoForSeason, runAlgoForAllSeasons


# backlogtodo optimize trueskill, glicko etc. for rapid iteration
# backlogtodo refactor equations here to be generic
def runTSForSeason(seasonCsv: str, winningBetThreshold: float= ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False):
    runAlgoForSeason(seasonCsv, ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH, ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH,
                     trueskillBeforeMatchPredictions, trueskillUpdateDataSingleTipoff, winningBetThreshold,
                     columnAdds=['Home TS Mu', 'Away TS Mu', 'Home TS Sigma', 'Away TS Sigma'], startFromBeginning=startFromBeginning)

# backlogtodo setup odds prediction to use Ev or win prob rather than bet threshold
def trueskillBeforeMatchPredictions(psd, homePlayerCode, awayPlayerCode, homeTeam, awayTeam, tipWinnerCode, scoringTeam, predictionArray=None, actualArray=None, histogramPredictionsDict=None,
                                    winningBetThreshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD):
    return beforeMatchPredictions(psd, homePlayerCode, awayPlayerCode, homeTeam, awayTeam, tipWinnerCode, scoringTeam, predictionArray=predictionArray, actualArray=actualArray, histogramPredictionsDict=histogramPredictionsDict, predictionSummaryPath=ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH,
                                  minimumTipWinPercentage=winningBetThreshold, predictionFunction=trueSkillTipWinProb, minimumAppearances=ENVIRONMENT.MIN_TS_APPEARANCES)

def runTSForAllSeasons(seasons, winningBetThreshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD):
    runAlgoForAllSeasons(seasons, ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH, ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH, trueskillBeforeMatchPredictions, trueskillUpdateDataSingleTipoff,
                         winningBetThreshold, columnAdds=['Home TS Mu', 'Away TS Mu', 'Home TS Sigma', 'Away TS Sigma'])

def trueskillUpdateDataSingleTipoff(psd, winnerCode, loserCode, homePlayerCode, game_code=None):
    if game_code:
        print(game_code)
    winnerCode = winnerCode[11:]
    loserCode = loserCode[11:]

    winnerOgMu = psd[winnerCode]["mu"]
    winnerOgSigma = psd[winnerCode]["sigma"]
    loserOgMu = psd[loserCode]["mu"]
    loserOgSigma = psd[loserCode]["sigma"]
    winnerMu, winnerSigma, loserMu, loserSigma = trueSkillMatchWithRawNums(psd[winnerCode]["mu"], psd[winnerCode]["sigma"], psd[loserCode]['mu'], psd[loserCode]["sigma"])
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

    print('Winner:', winnerCode, 'trueskill increased', winnerMu - winnerOgMu, 'to', winnerMu, '. Sigma is now', winnerSigma, '. W:', winnerWinCount, 'L', winnerAppearances - winnerWinCount)
    print('Loser:', loserCode, 'trueskill decreased', loserMu - loserOgMu, 'to', loserMu, '. Sigma is now', loserSigma, '. W:', loserAppearances - loserLosses, 'L', loserLosses)

    if homePlayerCode == winnerCode:
        homeMu = winnerOgMu
        homeSigma = winnerOgSigma
        awayMu = loserOgMu
        awaySigma = loserOgSigma
        homeAppearances = winnerAppearances - 1
        awayAppearances = loserAppearances - 1
        homeWins = winnerWinCount - 1
        homeLosses = psd[winnerCode]["losses"]
        awayWins = psd[loserCode]["wins"]
        awayLosses = loserLosses
    elif homePlayerCode == loserCode:
        homeMu = loserOgMu
        homeSigma = loserOgSigma
        awayMu = winnerOgMu
        awaySigma = winnerOgSigma
        awayAppearances = winnerAppearances
        homeAppearances = loserAppearances
        awayWins = winnerWinCount - 1
        awayLosses = psd[winnerCode]["losses"]
        homeWins = psd[loserCode]["wins"]
        homeLosses = loserLosses
    else:
        raise ValueError('neither code matches')

    return {"Home TS Mu": homeMu, "Home TS Sigma": homeSigma, "Away TS Mu": awayMu, "Away TS Sigma": awaySigma, "Home Lifetime Apperances": homeAppearances, "Away Lifetime Appearances": awayAppearances,
            "Home Tipper Wins": homeWins, "Home Tipper Losses": homeLosses, "Away Tipper Wins": awayWins, "Away Tipper Losses": awayLosses}

def calculateTrueSkillDictionaryFromZero():
    createPlayerTrueSkillDictionary() # clears the stored values,
    runTSForAllSeasons(ENVIRONMENT.ALL_SEASONS_LIST, winningBetThreshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD)
    print("\n", "trueskill dictionary updated for seasons", ENVIRONMENT.ALL_SEASONS_LIST, "\n")

def updateTrueSkillDictionaryFromLastGame():
    runTSForSeason(ENVIRONMENT.CURRENT_SEASON_CSV, winningBetThreshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False)
    print("\n", "trueskill dictionary updated from last game", "\n")

