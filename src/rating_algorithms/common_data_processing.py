import json
import pandas as pd
from sklearn.metrics import log_loss

import ENVIRONMENT
from src.database.database_creation import resetAndInitializePredictionSummaryDict

def preMatchPredictionsNoBinning(awayPlayerCode, awayPlayerTeam, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                 tipWinnerCode, winningBetThreshold, predictionSummaryPath, predictionArray, actualArray):
    with open(predictionSummaryPath) as dictFile:
        dsd = json.load(dictFile)

    if homeOdds > winningBetThreshold:
        if tipWinnerCode[11:] == homePlayerCode:
            dsd['correctTipoffPredictions'] += 1
            actualArray.append(1)
            if homePlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        else:
            dsd['incorrectTipoffPredictions'] += 1
            actualArray.append(0)
            if awayPlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        if homePlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
        else:
            dsd["losingBets"] += 1
        dsd['expectedTipWinsFromAlgo'] += homeOdds
        predictionArray.append(homeOdds)

    elif (1 - homeOdds) > winningBetThreshold:
        if tipWinnerCode[11:] == awayPlayerCode:
            dsd['correctTipoffPredictions'] += 1
            actualArray.append(1)
            if awayPlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        else:
            dsd['incorrectTipoffPredictions'] += 1
            actualArray.append(0)
            if homePlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        if awayPlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
        else:
            dsd['losingBets'] += 1
        dsd['expectedTipWinsFromAlgo'] += (1 - homeOdds)
        predictionArray.append(1-homeOdds)
    else:
        print('no bet, odds were not good enough')

    with open(predictionSummaryPath, 'w') as saveDictFile:
        json.dump(dsd, saveDictFile, indent=4)

    return predictionArray, actualArray

def histogramBinningPredictions(homeOdds, homePlayerCode, tipWinnerCode, homePlayerTeam, scoringTeam, predictionSummaryPath, predictionArray, actualArray, histogramPredictionsDict, minTipWinOdds=0.0):
    with open(predictionSummaryPath) as dictFile:
       dsd = json.load(dictFile)

    # divisions are based on the probability for the more likely player
    greaterOdds = homeOdds if homeOdds > 1-homeOdds else 1-homeOdds
    homeWinsTip = True if tipWinnerCode[11:] == homePlayerCode else False
    oddsBelongToHome = True if homeOdds > 1-homeOdds else False
    homeScoresFirst = True if homePlayerTeam == scoringTeam else False
    greaterOddsWinsTip = True if (homeWinsTip and oddsBelongToHome) or (not homeWinsTip and not oddsBelongToHome) else False
    predictionArray.append(greaterOdds)
    actualArray.append(greaterOddsWinsTip)

    for item in dsd['histogramDivisions']:
        if item['start'] < greaterOdds and item['end'] >= greaterOdds: # <= on greater prevents allows even odds bets. Setting a min appearances here would catch the unknown preds and stop them skewing
            subItem=item['predictionSummaries']
            subItem['totalMatchups'] += 1
            subItem['expectedTipWinsFromAlgo'] += greaterOdds
            histogramPredictionsDict[str(item['start'])]['predicted'] += [greaterOdds]
            histogramPredictionsDict[str(item['start'])]['actual'] += [greaterOddsWinsTip]

            if greaterOdds > minTipWinOdds:
                if homeScoresFirst and oddsBelongToHome:
                    subItem['winningBets'] += 1
                elif not homeScoresFirst and not oddsBelongToHome:
                    subItem['winningBets'] += 1
                else:
                    subItem['losingBets'] += 1

            if oddsBelongToHome:
                if homeScoresFirst:
                    subItem['higherOddsScoresFirst'] += 1
            else:
                if not homeScoresFirst:
                    subItem['higherOddsScoresFirst'] += 1

            if homeWinsTip:
                if homeScoresFirst:
                    subItem['tipWinnerScores'] += 1
                if oddsBelongToHome:
                    subItem['tipoffWinsByHigher'] += 1
                else:
                    subItem['tipoffLossesByHigher'] += 1
            else:
                if not homeScoresFirst:
                    subItem['tipWinnerScores'] += 1
                if not oddsBelongToHome:
                    subItem['tipoffWinsByHigher'] += 1
                else:
                    subItem['tipoffLossesByHigher'] += 1

            item['predictionSummaries'] = subItem

    with open(predictionSummaryPath, 'w') as saveDictFile:
        json.dump(dsd, saveDictFile)

    return predictionArray, actualArray, histogramPredictionsDict

def beforeMatchPredictions(psd, hTipCode, aTipCode, hTeam, aTeam, tipWinCode, scoringTeam, predictionArray, actualArray, histogramPredictionsDict,
                           minimumTipWinPercentage, predictionFunction, predictionSummaryPath, minimumAppearances):
    homeTipWinOdds = predictionFunction(hTipCode, aTipCode, psd=psd)

    if psd[hTipCode]['appearances'] > minimumAppearances and psd[aTipCode]['appearances'] > minimumAppearances:
        predictionArray, actualArray, histogramPredictionsDict = histogramBinningPredictions(homeTipWinOdds, hTipCode, tipWinCode, hTeam, scoringTeam, predictionSummaryPath,
                                                                   predictionArray, actualArray, histogramPredictionsDict, minTipWinOdds=minimumTipWinPercentage)
    else:
        print('no bet, not enough Data on participants')

    if psd[hTipCode]['appearances'] > minimumAppearances and psd[aTipCode]['appearances'] > minimumAppearances:
        preMatchPredictionsNoBinning(aTipCode, aTeam, homeTipWinOdds, hTipCode, hTeam, scoringTeam, tipWinCode, minimumTipWinPercentage,
                                     predictionSummaryPath, predictionArray, actualArray)
    else:
        print('no bet, not enough Data on participants')

    return predictionArray, actualArray, histogramPredictionsDict

def addSummaryMathToAlgoSummary(predictionSummariesPath, actualArray, predictionsArray, histogramPredictionsDict):
    with open(predictionSummariesPath) as wFile:
        dsd = json.load(wFile)

    logLossTotal = log_loss(actualArray, predictionsArray)
    dsd['logLoss'] = logLossTotal

    dsd["trueskillConstants"] = {
        "sigma": ENVIRONMENT.BASE_TS_SIGMA,
        "mu": ENVIRONMENT.BASE_TS_MU,
        "tau": ENVIRONMENT.BASE_TS_TAU,
        "beta": ENVIRONMENT.BASE_TS_BETA,
        "minAppearances": ENVIRONMENT.MIN_TS_APPEARANCES,
        "minTipWinOdds": ENVIRONMENT.TS_TIPOFF_ODDS_THRESHOLD
    },
    dsd["eloConstants"] = {
        "k_factor": ENVIRONMENT.K_FACTOR,
        "base_elo": ENVIRONMENT.BASE_ELO,
        "base_elo_beta": ENVIRONMENT.BASE_ELO_BETA,
        "minAppearances": ENVIRONMENT.MIN_ELO_APPEARANCES,
        "minTipWinOdds": ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD
    },
    dsd["glickoConstants"] = {
        "sigma": ENVIRONMENT.BASE_GLICKO_SIGMA,
        "mu": ENVIRONMENT.BASE_GLICKO_MU,
        "tau": ENVIRONMENT.BASE_GLICKO_TAU,
        "phi": ENVIRONMENT.BASE_GLICKO_PHI,
        "minAppearances": ENVIRONMENT.MIN_GLICKO_APPEARANCES,
        "minTipWinOdds": ENVIRONMENT.GLICKO_TIPOFF_ODDS_THRESHOLD
    },

    if dsd['winningBets'] + dsd['losingBets'] > 0:
        dsd['correctTipoffPredictionPercentage'] = dsd['correctTipoffPredictions'] / (dsd['correctTipoffPredictions'] + dsd['incorrectTipoffPredictions'])
        dsd['betWinPercentage'] = dsd['winningBets'] / (dsd['winningBets'] + dsd['losingBets'])
        dsd['expectedWinsFromTipWinPercentage'] = dsd['correctTipoffPredictionPercentage'] * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1 - dsd['correctTipoffPredictionPercentage']) * (1 - ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
    for histogramBin in dsd['histogramDivisions']:
        if histogramBin['predictionSummaries']['totalMatchups'] > 0:
            histogramBin['predictionSummaries']['tipWinPercentage'] = histogramBin['predictionSummaries']['tipoffWinsByHigher'] / histogramBin['predictionSummaries']['totalMatchups']
            histogramBin['predictionSummaries']['expectedTipWinPercentage'] = histogramBin['predictionSummaries']['expectedTipWinsFromAlgo'] / histogramBin['predictionSummaries']['totalMatchups']
            histogramBin['predictionSummaries']['tipWinnerScoresPercentage'] = histogramBin['predictionSummaries']['tipWinnerScores'] / histogramBin['predictionSummaries']['totalMatchups']
            histogramBin['predictionSummaries']['betWinPercentage'] = histogramBin['predictionSummaries']['winningBets'] / histogramBin['predictionSummaries']['totalMatchups']
            try:
                histogramBin['predictionSummaries']['logLoss'] = log_loss(histogramPredictionsDict[str(histogramBin['start'])]['actual'], histogramPredictionsDict[str(histogramBin['start'])]['predicted'])
            except:
                print('bin', histogramBin['start'], 'to', histogramBin['end'], 'likely has one value (0 or 1) and so may be breaking logloss.',
                      'The bin contained these values:')
                print('actual', histogramPredictionsDict[str(histogramBin['start'])]['actual'])
        else:
            print('No matchups for bin', histogramBin['start'], 'to', histogramBin['end'], '. Bin set empty')
            histogramBin['predictionSummaries'] = {"lol_lmao": "my b omg (no predictions in this bin)"}

    with open(predictionSummariesPath, 'w') as wFile:
        json.dump(dsd, wFile, indent=4)

def runAlgoForSeason(seasonCsv: str, skillDictPath: str, predictionSummariesPath: str, beforeMatchAlgo, algoSingleTipoff, winningBetThreshold: float,
                     predictionArray=None, actualArray=None, histogramPredictionsDict=None, columnAdds=None, startFromBeginning=False):
    df = pd.read_csv(seasonCsv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    if columnAdds is not None:
        df = dfEmptyColumnAdd(df, columnAdds)

    print('running for season doc', seasonCsv, '\n', '\n')
    colLen = len(df['Game Code'])

    with open(skillDictPath) as jsonFile:
        psd = json.load(jsonFile)

    if startFromBeginning:
        i = 0
    else:
        try:
            i = colLen - 1
            lastGameCode = psd['lastGameCode']
            while df.iloc[i]['Game Code'] != lastGameCode:
                i -= 1
            i += 1
        except:
            print('errror finding lastGameCode, starting from 0')
            i = 0

    while i < colLen:
        if df['Home Tipper'].iloc[i] != df['Home Tipper'].iloc[i]:
            i += 1
            continue
        hTip = df['Home Tipper'].iloc[i]
        tWinner = df['Tip Winner'].iloc[i]
        aTip = df['Away Tipper'].iloc[i]
        tWinLink = df['Tip Winner Link'].iloc[i]
        tLoseLink = df['Tip Loser Link'].iloc[i]
        if tWinner == hTip:
            hTipCode = tWinLink[11:]
            aTipCode = tLoseLink[11:]
        elif tWinner == aTip:
            hTipCode = tLoseLink[11:]
            aTipCode = tWinLink[11:]
        else:
            raise ValueError('no match for winner')

        if predictionArray is not None and actualArray is not None and histogramPredictionsDict is not None:
            with open(predictionSummariesPath) as file:
                dsd = json.load(file)

        scoringTeam = df['First Scoring Team'].iloc[i]
        hTeam = df['Home Short'].iloc[i]
        aTeam = df['Away Short'].iloc[i]

        if predictionArray is not None and actualArray is not None and histogramPredictionsDict is not None:
            predictionArray, actualArray, histogramPredictionsDict = beforeMatchAlgo(psd, hTipCode, aTipCode, hTeam, aTeam, tWinLink, scoringTeam,
                                                                                 predictionArray, actualArray, histogramPredictionsDict, winningBetThreshold)
        else:
            beforeMatchAlgo(psd, hTipCode, aTipCode, hTeam, aTeam, tWinLink, scoringTeam, winningBetThreshold)

        returnObj = algoSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])

        if columnAdds is not None:
            for key in returnObj.keys():
                df[key].iloc[i] = returnObj[key]

        i += 1

    psd['lastGameCode'] = df.iloc[-1]['Game Code']
    with open(skillDictPath, 'w') as write_file:
        json.dump(psd, write_file, indent=4)

    if predictionArray is not None and actualArray is not None and histogramPredictionsDict is not None:
        with open(predictionSummariesPath, 'w') as write_file:
            json.dump(dsd, write_file, indent=4)

    df.to_csv(str(seasonCsv)[:-4] + '-calculated-values.csv', index=False)

    if predictionArray is not None and actualArray is not None and histogramPredictionsDict is not None:
        return predictionArray, actualArray, histogramPredictionsDict

def runAlgoForAllSeasons(seasons, skillDictPath, predictionSummariesPath, algoPrematch, algoSingleTipoff, winningBetThreshold, columnAdds=None):
    seasonKey = ''
    histogramBinDivisions = list(range(50, 105, 5))
    histogramBinDivisions = [x/100 for x in histogramBinDivisions]
    print(histogramBinDivisions)
    dsd = resetAndInitializePredictionSummaryDict(histogramBinDivisions, predictionSummariesPath)

    predictionArray = list()
    actualArray = list()
    histogramPredictionsDict = {}

    for bin in dsd['histogramDivisions']:
        histogramPredictionsDict[str(bin['start'])] = {"actual": [], "predicted": []}

    for season in seasons:
        predictionArray, actualArray, histogramPredictionsDict = runAlgoForSeason(
            ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), skillDictPath, predictionSummariesPath,
            algoPrematch, algoSingleTipoff, winningBetThreshold, predictionArray, actualArray, histogramPredictionsDict, startFromBeginning=True, columnAdds=columnAdds)
        seasonKey += str(season) + '-'

    dsd['seasons'] = seasonKey + 'with-odds-' + str(winningBetThreshold)
    addSummaryMathToAlgoSummary(predictionSummariesPath, actualArray, predictionArray, histogramPredictionsDict)

    # with open(predictionSummariesPath, 'w') as predSum:
    #     json.dump(dsd, predSum, indent=4)

    print('ran algo for all seasons')

def dfEmptyColumnAdd(df, columns):
    for column in columns:
        df[column] = 0
    return df
