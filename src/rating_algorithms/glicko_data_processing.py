import json

import ENVIRONMENT

import pandas as pd

from src.database.database_creation import resetPredictionSummaries, createPlayerGlickoDictionary
from src.rating_algorithms.algorithms import glickoWinProb, glickoMatchWithRawNums

from src.rating_algorithms.common_data_processing import preMatchPredictions, beforeMatchPredictions, \
    addSummaryMathToAlgoSummary


def runGlickoForSeason(season: str, seasonCsv: str, playerSkillDictPath: str, winningBetThreshold: float=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False):
    df = pd.read_csv(seasonCsv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    # df['Home Mu'] = None
    # df['Home Sigma'] = None
    # df['Away Mu'] = None
    # df['Away Sigma'] = None

    winningBets = 0
    losingBets = 0

    print('running for season doc', seasonCsv, '\n', '\n')
    colLen = len(df['Game Code'])

    with open(playerSkillDictPath) as jsonFile:
        psd = json.load(jsonFile)

    if startFromBeginning:
        i = 0
    else:
        i = colLen - 1
        lastGameCode = psd['lastGameCode']
        while df.iloc[i]['Game Code'] != lastGameCode:
            i -= 1
        i += 1

    with open(ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH) as jsonFile:
        dsd = json.load(jsonFile)

    while i < colLen:
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

        glickoBeforeMatchPredictions(season, psd, dsd, hTipCode, aTipCode, tWinLink, df['First Scoring Team'].iloc[i], winningBetThreshold)
        glickoUpdateDataSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])
        # df['Home Mu'].iloc[i] = homeMu
        # df['Home Sigma'].iloc[i] = homeSigma
        # df['Away Mu'].iloc[i] = awayMu
        # df['Away Sigma'].iloc[i] = awaySigma

        i += 1

    # if startFromBeginning:
    #     allKeys = psd.keys()
    #     for key in allKeys:
    #         key['sigma'] += 2
    #         if key['sigma'] > 8.333333333333334:
    #             key['sigma'] = 8.333333333333334
    #     print('added 2 to all sigmas for new season')

    psd['lastGameCode'] = df.iloc[-1]['Game Code']
    with open(playerSkillDictPath, 'w') as write_file:
        json.dump(psd, write_file, indent=4)

    with open(ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH, 'w') as write_file:
        json.dump(dsd, write_file, indent=4)

    # df.to_csv(str(seasonCsv)[:-4] + '-test.csv')

    return winningBets, losingBets

def glickoBeforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD):
    beforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold=winningBetThreshold, predictionFunction=glickoWinProb)

def runGlickoForAllSeasons(seasons, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD):
    seasonKey = ''
    for season in seasons:
        runGlickoForSeason(season, ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season),
                           ENVIRONMENT.PLAYER_GLICKO_DICT_PATH, winningBetThreshold, startFromBeginning=True)
        seasonKey += str(season) + '-'

    with open(ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH) as predSum:
        dsd = json.load(predSum)

    dsd['seasons'] = seasonKey + 'with-odds-' + str(winningBetThreshold)
    dsd = addSummaryMathToAlgoSummary(dsd)

    with open(ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH, 'w') as predSum:
        json.dump(dsd, predSum, indent=4)

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

    # if homePlayerCode == winnerCode:
    #     homeMu = winnerOgMu
    #     homeSigma = winnerOgSigma
    #     awayMu = loserOgMu
    #     awaySigma = loserOgSigma
    # elif homePlayerCode == loserCode:
    #     homeMu = loserOgMu
    #     homeSigma = loserOgSigma
    #     awayMu = winnerOgMu
    #     awaySigma = winnerOgSigma

    # return homeMu, homeSigma, awayMu, awaySigma

def calculateGlickoDictionaryFromZero():
    resetPredictionSummaries(ENVIRONMENT.GLICKO_PREDICTION_SUMMARIES_PATH) # reset sums
    createPlayerGlickoDictionary() # clears the stored values,
    runGlickoForAllSeasons(ENVIRONMENT.ALL_SEASONS_LIST, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD)
    print('\n', 'trueskill dictionary updated for seasons', ENVIRONMENT.ALL_SEASONS_LIST, '\n')

def updateGlickoDictionaryFromLastGame():
    runGlickoForSeason(ENVIRONMENT.CURRENT_SEASON, ENVIRONMENT.CURRENT_SEASON_CSV, ENVIRONMENT.PLAYER_GLICKO_DICT_PATH, winningBetThreshold=ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False)
    print('\n', 'trueskill dictionary updated from last game', '\n')
