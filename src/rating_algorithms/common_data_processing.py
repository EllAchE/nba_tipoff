import json
import pandas as pd

import ENVIRONMENT
from src.database.database_access import getPlayerTeamInSeasonFromBballRefLink
from src.database.database_creation import resetAndInitializePredictionSummaryDict


def preMatchPredictionsNoBinning(awayPlayerCode, awayPlayerTeam, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                 tipWinnerCode, winningBetThreshold, predictionSummaryPath):
    with open(predictionSummaryPath) as dictFile:
        dsd = json.load(dictFile)

    if homeOdds > winningBetThreshold:
        if tipWinnerCode[11:] == homePlayerCode:
            dsd['correctTipoffPredictions'] += 1
            if homePlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        else:
            dsd['incorrectTipoffPredictions'] += 1
            if awayPlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        if homePlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
        else:
            dsd["losingBets"] += 1
        dsd['expectedWinsFromAlgo'] += homeOdds
    elif (1 - homeOdds) > winningBetThreshold:
        if tipWinnerCode[11:] == awayPlayerCode:
            dsd['correctTipoffPredictions'] += 1
            if awayPlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        else:
            dsd['incorrectTipoffPredictions'] += 1
            if homePlayerTeam == scoringTeam:
                dsd['tipWinnerScores'] += 1
        if awayPlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
        else:
            dsd['losingBets'] += 1
        dsd['expectedWinsFromAlgo'] += (1 - homeOdds)
    else:
        print('no bet, odds were not good enough')

    with open(predictionSummaryPath, 'w') as saveDictFile:
        json.dump(dsd, saveDictFile, indent=4)

def histogramBinningPredictions(homeOdds, homePlayerCode, tipWinnerCode, homePlayerTeam, scoringTeam, predictionSummaryPath, minTipWinOdds=0.0):
    with open(predictionSummaryPath) as dictFile:
       dsd = json.load(dictFile)

    # divisions are based on the probability for the more likely player
    greaterOdds = homeOdds if homeOdds > 1-homeOdds else 1-homeOdds
    if greaterOdds < minTipWinOdds:
        return None
    homeWinsTip = True if tipWinnerCode[11:] == homePlayerCode else False
    oddsBelongToHome = True if homeOdds > 1-homeOdds else False
    homeScoresFirst = True if homePlayerTeam == scoringTeam else False
    for item in dsd['histogramDivisions']:
        if item['start'] < greaterOdds and item['end'] >= greaterOdds: # <= on greater prevents allows even odds bets. Setting a min appearances here would catch the unknown preds and stop them skewing
            subItem=item['predictionSummaries']
            subItem['totalMatchups'] += 1
            subItem['expectedWinsFromAlgo'] += greaterOdds
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
            if homeWinsTip and not homeScoresFirst:
                print('case')
            elif not homeWinsTip and homeScoresFirst:
                print('case')


    with open(predictionSummaryPath, 'w') as saveDictFile:
        json.dump(dsd, saveDictFile)

def beforeMatchPredictions(season, psd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam,
                           minimumTipWinPercentage, predictionFunction, predictionSummaryPath):
    homeOdds = predictionFunction(homePlayerCode, awayPlayerCode, psd=psd)
    homePlayerTeam = getPlayerTeamInSeasonFromBballRefLink(homePlayerCode, season, longCode=False)['currentTeam']
    awayPlayerTeam = getPlayerTeamInSeasonFromBballRefLink(awayPlayerCode, season, longCode=False)['currentTeam']

    histogramBinningPredictions(homeOdds, homePlayerCode, tipWinnerCode, homePlayerTeam, scoringTeam, predictionSummaryPath, minTipWinOdds=minimumTipWinPercentage)

    if psd[homePlayerCode]['appearances'] > minimumTipWinPercentage and psd[awayPlayerCode]['appearances'] > minimumTipWinPercentage:
        preMatchPredictionsNoBinning(awayPlayerCode, awayPlayerTeam, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                                     tipWinnerCode, minimumTipWinPercentage, predictionSummaryPath)
    else:
        print('no bet, not enough Data on participants')

def addSummaryMathToAlgoSummary(predictionSummariesPath):
    with open(predictionSummariesPath) as wFile:
        dsd = json.load(wFile)

    dsd["trueskillConstants"] = {
        "sigma": ENVIRONMENT.BASE_TS_SIGMA,
        "mu": ENVIRONMENT.BASE_TS_MU,
        "rd": ENVIRONMENT.BASE_TS_RD,
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
        dsd['winPercentage'] = dsd['winningBets'] / (dsd['winningBets'] + dsd['losingBets'])
        dsd['expectedWinsFromTipWinPercentage'] = dsd['correctTipoffPredictionPercentage'] * ENVIRONMENT.TIP_WINNER_SCORE_ODDS + (1-dsd['correctTipoffPredictionPercentage']) * (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
    for histogramBin in dsd['histogramDivisions']:
        if histogramBin['predictionSummaries']['totalMatchups'] > 0:
            histogramBin['predictionSummaries']['winPercentage'] = histogramBin['predictionSummaries']['tipoffWinsByHigher'] / histogramBin['predictionSummaries']['totalMatchups']
            histogramBin['predictionSummaries']['expectedWinPercentage'] = histogramBin['predictionSummaries']['expectedWinsFromAlgo'] / histogramBin['predictionSummaries']['totalMatchups']
            histogramBin['predictionSummaries']['tipWinnerScoresPercentage'] = histogramBin['predictionSummaries']['tipWinnerScores'] / histogramBin['predictionSummaries']['totalMatchups']
        else:
            print('No matchups for bin', histogramBin['start'], 'to', histogramBin['end'])

    with open(predictionSummariesPath, 'w') as wFile:
        json.dump(dsd, wFile, indent=4)

def runAlgoForSeason(season: str, seasonCsv: str, skillDictPath: str, predictionSummariesPath: str, algoPrematch, algoSingleTipoff, winningBetThreshold: float,
                      columnAdds=None, startFromBeginning=False):
    df = pd.read_csv(seasonCsv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    if columnAdds is not None:
        df = dfEmptyColumnAdd(df, columnAdds)

    winningBets = losingBets = 0

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

        with open(predictionSummariesPath) as file:
            dsd = json.load(file)

        scoringTeam = df['First Scoring Team'].iloc[i]

        algoPrematch(season, psd, hTipCode, aTipCode, tWinLink, scoringTeam, winningBetThreshold)
        returnObj = algoSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])

        # with open(predictionSummariesPath, 'w') as writeFile:
        #     json.dump(dsd, writeFile, indent=4)

        if columnAdds is not None:
            for key in returnObj.keys():
                df[key] = returnObj[key]

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
    with open(skillDictPath, 'w') as write_file:
        json.dump(psd, write_file, indent=4)

    with open(predictionSummariesPath, 'w') as write_file:
        json.dump(dsd, write_file, indent=4)

    df.to_csv(str(seasonCsv)[:-4] + '-test.csv')

    return winningBets, losingBets

def runAlgoForAllSeasons(seasons, skillDictPath, predictionSummariesPath, algoPrematch, algoSingleTipoff, winningBetThreshold, columnAdds=None):
    seasonKey = ''
    histogramBinDivisions = list(range(50, 105, 5))
    histogramBinDivisions = [x/100 for x in histogramBinDivisions]
    print(histogramBinDivisions)
    dsd = resetAndInitializePredictionSummaryDict(histogramBinDivisions, predictionSummariesPath)
    for season in seasons:
        runAlgoForSeason(season, ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), skillDictPath, predictionSummariesPath, algoPrematch, algoSingleTipoff, winningBetThreshold,
                          startFromBeginning=True, columnAdds=columnAdds)
        seasonKey += str(season) + '-'

    dsd['seasons'] = seasonKey + 'with-odds-' + str(winningBetThreshold)
    addSummaryMathToAlgoSummary(predictionSummariesPath)

    # with open(predictionSummariesPath, 'w') as predSum:
    #     json.dump(dsd, predSum, indent=4)

    print('ran algo for all seasons')

def dfEmptyColumnAdd(df, columns):
    for column in columns:
        df[column] = None
    return df
