import ENVIRONMENT
from src.database.database_creation import createPlayerEloDictionary
from src.skill_algorithms.algorithms import eloMatchWithRawNums, eloTipWinProb
from src.skill_algorithms.common_data_processing import beforeMatchPredictions, \
    runAlgoForSeason, runAlgoForAllSeasons


def runEloForSeason(season: str, seasonCsv: str, winningBetThreshold: float= ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False):
    runAlgoForSeason(season, seasonCsv, winningBetThreshold, columnAdds=["Home Elo", "Away Elo"], startFromBeginning=startFromBeginning)

def eloBeforeMatchPredictions(psd, hTipCode, aTipCode, hTeam, aTeam, tWinLink, scoringTeam, predictionArray, actualArray, histogramPredictionsDict, winningBetThreshold=ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD):
    return beforeMatchPredictions(psd, hTipCode, aTipCode, hTeam, aTeam, tWinLink, scoringTeam, predictionArray, actualArray, histogramPredictionsDict, minimumTipWinPercentage=winningBetThreshold,
                                  predictionSummaryPath=ENVIRONMENT.ELO_PREDICTION_SUMMARIES_PATH, predictionFunction=eloTipWinProb, minimumAppearances=ENVIRONMENT.MIN_ELO_APPEARANCES)

def runEloForAllSeasons(seasons, winningBetThreshold=ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD):
    runAlgoForAllSeasons(seasons, ENVIRONMENT.PLAYER_ELO_DICT_PATH, ENVIRONMENT.ELO_PREDICTION_SUMMARIES_PATH, eloBeforeMatchPredictions,
                         eloUpdateDataSingleTipoff, winningBetThreshold, columnAdds=['Home Elo', 'Away Elo'])

def eloUpdateDataSingleTipoff(psd, winnerCode, loserCode, homePlayerCode, game_code=None):
    if game_code:
        print(game_code)
    winnerCode = winnerCode[11:]
    loserCode = loserCode[11:]

    winnerOgElo = psd[winnerCode]["elo"]
    loserOgElo = psd[loserCode]["elo"]
    winnerElo, loserElo = eloMatchWithRawNums(psd[winnerCode]["elo"], psd[loserCode]['elo'])
    winnerWinCount = psd[winnerCode]["wins"] + 1
    winnerAppearances = psd[winnerCode]["appearances"] + 1
    loserLosses = psd[loserCode]["losses"] + 1
    loserAppearances = psd[loserCode]["appearances"] + 1

    psd[winnerCode]["wins"] = winnerWinCount
    psd[winnerCode]["appearances"] = winnerAppearances
    psd[loserCode]["losses"] = loserLosses
    psd[loserCode]["appearances"] = loserAppearances
    psd[winnerCode]["elo"] = winnerElo
    psd[loserCode]["elo"] = loserElo

    print('Winner:', winnerCode, 'elo increased', winnerElo - winnerOgElo, 'to', winnerElo, '. W:', winnerWinCount, 'L', winnerAppearances - winnerWinCount)
    print('Loser:', loserCode, 'elo decreased', loserElo - loserOgElo, 'to', loserElo, '. W:', loserAppearances - loserLosses, 'L', loserLosses)

    if homePlayerCode == winnerCode:
        homeElo = winnerOgElo
        awayElo = loserOgElo
    elif homePlayerCode == loserCode:
        homeElo = loserOgElo
        awayElo = winnerOgElo

    return {"Home Elo": homeElo, "Away Elo": awayElo}

def calculateEloDictionaryFromZero():
    createPlayerEloDictionary() # clears the stored values,
    runEloForAllSeasons(ENVIRONMENT.ALL_SEASONS_LIST, winningBetThreshold=ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD)
    print("\n", "elo dictionary updated for seasons", ENVIRONMENT.ALL_SEASONS_LIST, "\n")

def updateEloDictionaryFromLastGame():
    runEloForSeason(ENVIRONMENT.CURRENT_SEASON, ENVIRONMENT.CURRENT_SEASON_CSV, ENVIRONMENT.PLAYER_ELO_DICT_PATH, winningBetThreshold=ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False)
    print("\n", "elo dictionary updated from last game", "\n")
