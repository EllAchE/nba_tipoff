import json

import ENVIRONMENT

import pandas as pd

from src.database.database_creation import resetPredictionSummaries, createPlayerTrueSkillDictionary
from src.rating_algorithms.algorithms import trueSkillMatchWithRawNums, trueSkillWinProb
from src.rating_algorithms.common_data_processing import preMatchPredictions, beforeMatchPredictions, \
    addSummaryMathToAlgoSummary


# backlogtodo optimize trueskill, glicko etc. for rapid iteration
# backlogtodo refactor equations here to be generic
def runTSForSeason(season: str, seasonCsv: str, playerSkillDictPath: str, winningBetThreshold: float=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False):
    df = pd.read_csv(seasonCsv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    df['Home Mu'] = None
    df['Home Sigma'] = None
    df['Away Mu'] = None
    df['Away Sigma'] = None

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

    with open(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH) as jsonFile:
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

        trueskillBeforeMatchPredictions(season, psd, dsd, hTipCode, aTipCode, tWinLink, df['First Scoring Team'].iloc[i], winningBetThreshold)
        homeMu, homeSigma, awayMu, awaySigma = trueSkillUpdateDataSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])
        df['Home Mu'].iloc[i] = homeMu
        df['Home Sigma'].iloc[i] = homeSigma
        df['Away Mu'].iloc[i] = awayMu
        df['Away Sigma'].iloc[i] = awaySigma

        i += 1

    # if startFromBeginning:
    #     allKeys = psd.keys()
    #     for key in allKeys:
    #         key['sigma'] += 2
    #         #todo place where season end sigma is udpated. Can toggle this to different effects
    #         if key['sigma'] > 8.333333333333334:
    #             key['sigma'] = 8.333333333333334
    #     print("added 2 to all sigmas for new season")

    psd['lastGameCode'] = df.iloc[-1]['Game Code']
    with open(playerSkillDictPath, 'w') as write_file:
        json.dump(psd, write_file, indent=4)

    with open(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH, 'w') as write_file:
        json.dump(dsd, write_file, indent=4)

    df.to_csv(str(seasonCsv)[:-4] + '-test.csv')

    return winningBets, losingBets

# backlogtodo setup odds prediction to use Ev or win prob rather than bet threshold
def trueskillBeforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD):
    beforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold=winningBetThreshold, predictionFunction=trueSkillWinProb)

def runTSForAllSeasons(seasons, winning_bet_threshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD):
    seasonKey = ''
    for season in seasons:
        runTSForSeason(season, ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season),
                       ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH, winning_bet_threshold, startFromBeginning=True)
        seasonKey += str(season) + '-'

    with open(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH) as predSum:
        dsd = json.load(predSum)

    dsd['seasons'] = seasonKey + 'with-odds-' + str(winning_bet_threshold)
    dsd = addSummaryMathToAlgoSummary(dsd)

    with open(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH, 'w') as predSum:
        json.dump(dsd, predSum, indent=4)

def trueSkillUpdateDataSingleTipoff(psd, winnerCode, loserCode, homePlayerCode, game_code=None):
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
    elif homePlayerCode == loserCode:
        homeMu = loserOgMu
        homeSigma = loserOgSigma
        awayMu = winnerOgMu
        awaySigma = winnerOgSigma

    return homeMu, homeSigma, awayMu, awaySigma

def calculateTrueSkillDictionaryFromZero():
    resetPredictionSummaries(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH) # reset sums
    createPlayerTrueSkillDictionary() # clears the stored values,
    runTSForAllSeasons(ENVIRONMENT.ALL_SEASONS_LIST, winning_bet_threshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD)
    print("\n", "trueskill dictionary updated for seasons", ENVIRONMENT.ALL_SEASONS_LIST, "\n")

def updateTrueSkillDictionaryFromLastGame():
    runTSForSeason(ENVIRONMENT.CURRENT_SEASON, ENVIRONMENT.CURRENT_SEASON_CSV, ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH, winningBetThreshold=ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False)
    print("\n", "trueskill dictionary updated from last game", "\n")
