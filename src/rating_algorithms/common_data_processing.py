import json
import pandas as pd

import ENVIRONMENT
from src.database.database_access import getPlayerTeamInSeasonFromBballRefLink

def preMatchPredictionsNoBinning(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                 tipWinnerCode, winningBetThreshold):
    totalBets = dsd['winningBets'] + dsd['losingBets']
    if homeOdds > winningBetThreshold:
        if tipWinnerCode[11:] == homePlayerCode:
            dsd['correctTipoffPredictions'] += 1
        else:
            dsd['incorrectTipoffPredictions'] += 1
        if homePlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
        else:
            dsd["losingBets"] += 1
        dsd['predictionAverage'] = (dsd['predictionAverage'] * totalBets + homeOdds) / (totalBets + 1)
    elif (1 - homeOdds) > winningBetThreshold:
        if tipWinnerCode[11:] == awayPlayerCode:
            dsd['correctTipoffPredictions'] += 1
        else:
            dsd['incorrectTipoffPredictions'] += 1
        if awayPlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
        else:
            dsd['losingBets'] += 1
        dsd['predictionAverage'] = (dsd['predictionAverage'] * totalBets + (1 - homeOdds)) / (totalBets + 1)
    else:
        print('no bet, odds were not good enough')

def createEmptySummaryDictionary():
    return {
        "correctTipoffPredictions": None,
        "incorrectTipoffPredictions": None,
        "correctTipoffPredictionPercentage": None,
        "winningBets": None,
        "losingBets": None,
        "winPercentage": None,
        "expectedWinsFromTip": None,
        "predictionAverage": None,
        "totalMatchups": None,
    }

def histogramBinningPredictions(awayPlayerCode, awayPlayerTeam, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                tipWinnerCode):
    histogramBinDivisions = range(0.5, 1, 0.05) # divisions are based on the probability for the more likely player
    intervalList = list()
    i = 0
    lstLen = len(histogramBinDivisions)
    while i < lstLen - 2:
        dsd = createEmptySummaryDictionary()
        preMatchPredictionsNoBinning(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                     tipWinnerCode)
        intervalList.append({
            "start": histogramBinDivisions[i],
            "end": histogramBinDivisions[i + 1],
            "predictionSummaries": dsd
        })


def beforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, minimumTipWinPercentage, predictionFunction):
    homeOdds = predictionFunction(homePlayerCode, awayPlayerCode, psd=psd)
    homePlayerTeam = getPlayerTeamInSeasonFromBballRefLink(homePlayerCode, season, longCode=False)['currentTeam']
    awayPlayerTeam = getPlayerTeamInSeasonFromBballRefLink(awayPlayerCode, season, longCode=False)['currentTeam']

    histogramBinningPredictions(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam, tipWinnerCode)

    if psd[homePlayerCode]['appearances'] > minimumTipWinPercentage and psd[awayPlayerCode]['appearances'] > minimumTipWinPercentage:
        preMatchPredictionsNoBinning(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                     tipWinnerCode, minimumTipWinPercentage)
    else:
        print('no bet, not enough Data on participants')

def addSummaryMathToAlgoSummary(dsd):
    dsd['correctTipoffPredictionPercentage'] = dsd['correctTipoffPredictions'] / (dsd['correctTipoffPredictions'] + dsd['incorrectTipoffPredictions'])
    dsd['winPercentage'] = dsd['winningBets'] / (dsd['winningBets'] + dsd['losingBets'])
    dsd['expectedWinsFromTip'] = dsd['correctTipoffPredictionPercentage'] * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1-dsd['correctTipoffPredictionPercentage']) * (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
    return dsd

def runAlgoForSeason(season: str, seasonCsv: str, playerSkillDictPath: str, predictionSummariesPath: str, algoPrematch,
                     algoSingleTipoff, winningBetThreshold, columnAddAlgo=None, startFromBeginning=False):
    df = pd.read_csv(seasonCsv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    if columnAddAlgo is not None:
        df = columnAddAlgo(df)

    winningBets = losingBets = 0

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

    with open(predictionSummariesPath) as jsonFile:
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

        algoPrematch(season, psd, dsd, hTipCode, aTipCode, tWinLink, df['First Scoring Team'].iloc[i], winningBetThreshold)
        homeMu, homeSigma, awayMu, awaySigma = algoSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])
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

    with open(predictionSummariesPath, 'w') as write_file:
        json.dump(dsd, write_file, indent=4)

    df.to_csv(str(seasonCsv)[:-4] + '-test.csv')

    return winningBets, losingBets
